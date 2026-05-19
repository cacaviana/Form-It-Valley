import csv
import io
import re
from datetime import datetime, timezone
from typing import Optional


REQUIRED_HEADERS = ["email", "ddi", "ddd", "numero"]
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
DIGITS_ONLY = re.compile(r"\D+")


class BlacklistFactory:
    """Parse CSV, normaliza entradas e cria documentos de blacklist."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def normalize_email(email: Optional[str]) -> Optional[str]:
        if not email:
            return None
        cleaned = email.strip().lower()
        if not EMAIL_REGEX.match(cleaned):
            return None
        return cleaned

    @staticmethod
    def digits_only(value: Optional[str]) -> str:
        if not value:
            return ""
        return DIGITS_ONLY.sub("", value)

    @classmethod
    def normalize_phone(cls, ddi: Optional[str], ddd: Optional[str], numero: Optional[str]) -> Optional[str]:
        ddi_d = cls.digits_only(ddi)
        ddd_d = cls.digits_only(ddd)
        numero_d = cls.digits_only(numero)
        if not numero_d:
            return None
        return f"{ddi_d}{ddd_d}{numero_d}"

    @classmethod
    def parse_csv(cls, csv_text: str) -> tuple[list[dict], list[str]]:
        """Le o CSV e retorna (entries_validas, lista_de_erros).

        Header obrigatorio: email,ddi,ddd,numero (qualquer ordem nao e permitida).
        Cada linha deve ter pelo menos email OU telefone preenchido.
        """
        errors: list[str] = []
        entries: list[dict] = []

        if not csv_text or not csv_text.strip():
            errors.append("CSV vazio")
            return entries, errors

        try:
            reader = csv.DictReader(io.StringIO(csv_text))
        except Exception as exc:
            errors.append(f"CSV mal formatado: {exc}")
            return entries, errors

        headers = [h.strip().lower() for h in (reader.fieldnames or [])]
        if headers != REQUIRED_HEADERS:
            errors.append(
                f"Header invalido. Esperado: {','.join(REQUIRED_HEADERS)}. Recebido: {','.join(headers) or '(vazio)'}"
            )
            return entries, errors

        seen: set[tuple[Optional[str], Optional[str]]] = set()

        for idx, row in enumerate(reader, start=2):  # linha 1 = header
            email = cls.normalize_email((row.get("email") or "").strip())
            phone = cls.normalize_phone(row.get("ddi"), row.get("ddd"), row.get("numero"))

            if not email and not phone:
                errors.append(f"Linha {idx}: sem email valido nem telefone")
                continue

            # Detecta email mal formatado quando o admin informou algo no campo
            raw_email = (row.get("email") or "").strip()
            if raw_email and not email:
                errors.append(f"Linha {idx}: email invalido '{raw_email}'")
                continue

            key = (email, phone)
            if key in seen:
                continue
            seen.add(key)
            entries.append({"email": email, "phone": phone})

        return entries, errors

    @classmethod
    def create_document(
        cls,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        entries: list[dict],
        uploaded_by: Optional[str] = None,
    ) -> dict:
        now = cls._now_iso()
        return {
            "tenant_id": tenant_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "entries": entries,
            "total_entries": len(entries),
            "csv_uploaded_at": now,
            "csv_uploaded_by": uploaded_by,
            "created_at": now,
            "updated_at": now,
        }

    @classmethod
    def create_blocked_attempt(
        cls,
        tenant_id: str,
        flow_id: str,
        email: Optional[str],
        phone: Optional[str],
        matched_field: str,
    ) -> dict:
        return {
            "tenant_id": tenant_id,
            "flow_id": flow_id,
            "email": email,
            "phone": phone,
            "matched_field": matched_field,
            "blocked_at": cls._now_iso(),
        }
