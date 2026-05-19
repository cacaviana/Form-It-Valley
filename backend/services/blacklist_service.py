from typing import Optional
from data.repositories.mongo.blacklist_repository import BlacklistRepository
from data.repositories.mongo.blocked_attempts_repository import BlockedAttemptsRepository
from factories.blacklist_factory import BlacklistFactory
from mappers.blacklist_mapper import BlacklistMapper, BlockedAttemptMapper


class BlacklistService:
    """Orquestra upload, leitura e checagem de leads contra a lista negra."""

    def __init__(self):
        self._repo = BlacklistRepository()
        self._attempts = BlockedAttemptsRepository()
        self._factory = BlacklistFactory
        self._mapper = BlacklistMapper
        self._attempt_mapper = BlockedAttemptMapper

    async def upload(
        self,
        csv_text: str,
        scope_type: str,
        scope_id: str,
        tenant_id: str,
        uploaded_by: Optional[str] = None,
    ) -> dict:
        entries, errors = self._factory.parse_csv(csv_text)
        if not entries:
            return {
                "ok": False,
                "errors": errors or ["Nenhuma entrada valida no CSV"],
                "skipped_lines": len(errors),
            }

        doc = self._factory.create_document(
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
            entries=entries,
            uploaded_by=uploaded_by,
        )
        saved = await self._repo.upsert(doc)
        return {
            "ok": True,
            "blacklist_id": str(saved["_id"]),
            "total_entries": saved["total_entries"],
            "skipped_lines": len(errors),
            "errors": errors,
            "csv_uploaded_at": saved["csv_uploaded_at"],
        }

    async def get_metadata(self, scope_type: str, scope_id: str) -> Optional[dict]:
        doc = await self._repo.find_by_scope(scope_type, scope_id)
        if not doc:
            return None
        return self._mapper.to_metadata(doc)

    async def delete(self, scope_type: str, scope_id: str) -> int:
        return await self._repo.delete_by_scope(scope_type, scope_id)

    async def list_entries(self, scope_type: str, scope_id: str) -> list[dict]:
        """Retorna as entries (email + telefone). Uso apenas por admin autenticado."""
        doc = await self._repo.find_by_scope(scope_type, scope_id)
        if not doc:
            return []
        return doc.get("entries", [])

    async def add_entry(
        self,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        email: Optional[str],
        ddi: Optional[str],
        ddd: Optional[str],
        numero: Optional[str],
    ) -> dict:
        norm_email = self._factory.normalize_email(email)
        norm_phone = self._factory.normalize_phone(ddi, ddd, numero)
        if not norm_email and not norm_phone:
            return {"ok": False, "error": "Forneca email valido ou telefone"}

        doc = await self._repo.find_by_scope(scope_type, scope_id)
        if not doc:
            # Cria a blacklist com 1 entry
            new_doc = self._factory.create_document(
                tenant_id=tenant_id,
                scope_type=scope_type,
                scope_id=scope_id,
                entries=[{"email": norm_email, "phone": norm_phone}],
            )
            saved = await self._repo.upsert(new_doc)
            return {"ok": True, "total_entries": saved["total_entries"]}

        entries = doc.get("entries", [])
        # Dedup: nao duplica mesma chave
        if any((e.get("email") == norm_email and e.get("phone") == norm_phone) for e in entries):
            return {"ok": False, "error": "Entrada ja existe"}

        entries.append({"email": norm_email, "phone": norm_phone})
        doc["entries"] = entries
        doc["total_entries"] = len(entries)
        doc["updated_at"] = self._factory._now_iso()
        saved = await self._repo.upsert(doc)
        return {"ok": True, "total_entries": saved["total_entries"]}

    async def remove_entry(
        self,
        scope_type: str,
        scope_id: str,
        email: Optional[str],
        phone: Optional[str],
    ) -> dict:
        """Remove uma entry exata (email + phone normalizados)."""
        norm_email = self._factory.normalize_email(email) if email else None
        # phone aqui ja deve vir normalizado (frontend manda assim) ou vai como string crua
        norm_phone = self._factory.digits_only(phone) if phone else None

        doc = await self._repo.find_by_scope(scope_type, scope_id)
        if not doc:
            return {"ok": False, "error": "Lista nao encontrada"}

        entries = doc.get("entries", [])
        before = len(entries)
        entries = [e for e in entries if not (e.get("email") == norm_email and e.get("phone") == norm_phone)]
        if len(entries) == before:
            return {"ok": False, "error": "Entrada nao encontrada"}

        doc["entries"] = entries
        doc["total_entries"] = len(entries)
        doc["updated_at"] = self._factory._now_iso()
        await self._repo.upsert(doc)
        return {"ok": True, "total_entries": len(entries)}

    async def list_attempts(self, flow_id: str) -> list[dict]:
        docs = await self._attempts.find_by_flow(flow_id)
        return [self._attempt_mapper.to_response(d) for d in docs]

    async def check_lead(
        self,
        flow_id: str,
        tenant_id: str,
        email: Optional[str],
        ddi: Optional[str],
        ddd: Optional[str],
        numero: Optional[str],
    ) -> dict:
        """Compara dados do lead contra a blacklist do flow.

        Match em qualquer campo (email OU telefone) ja bloqueia.
        Se bloqueado, salva auditoria em blocked_attempts.
        """
        norm_email = self._factory.normalize_email(email)
        norm_phone = self._factory.normalize_phone(ddi, ddd, numero)

        # Sem dados pra comparar — nao bloqueia
        if not norm_email and not norm_phone:
            return {"blocked": False, "matched_field": None}

        bl = await self._repo.find_by_scope("flow", flow_id)
        if not bl:
            return {"blocked": False, "matched_field": None}

        matched_field: Optional[str] = None
        for entry in bl.get("entries", []):
            entry_email = entry.get("email")
            entry_phone = entry.get("phone")

            if norm_email and entry_email and entry_email == norm_email:
                matched_field = "email"
                break

            if norm_phone and entry_phone:
                # Match exato OU substring no final (caso lead nao informe DDI)
                if entry_phone == norm_phone or entry_phone.endswith(norm_phone) or norm_phone.endswith(entry_phone):
                    matched_field = "phone"
                    break

        if matched_field:
            attempt = self._factory.create_blocked_attempt(
                tenant_id=tenant_id,
                flow_id=flow_id,
                email=norm_email,
                phone=norm_phone,
                matched_field=matched_field,
            )
            await self._attempts.insert(attempt)
            return {"blocked": True, "matched_field": matched_field}

        return {"blocked": False, "matched_field": None}
