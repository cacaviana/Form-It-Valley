import json
import re
import logging
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config.settings import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TIMEZONE = ZoneInfo("America/Sao_Paulo")

# Ordem fixa das colunas escritas na planilha (A..L)
HEADERS = [
    "Data Entrada",
    "Nome",
    "Email",
    "Telefone",
    "Formulario",
    "Data Agendamento",
    "Hora Agendamento",
    "UTM Source",
    "UTM Medium",
    "UTM Campaign",
    "UTM Content",
    "UTM Term",
]

# Colunas de agendamento (F e G, 0-indexed 5 e 6)
COL_EMAIL = 2
COL_DATA_AGENDAMENTO = "F"
COL_HORA_AGENDAMENTO = "G"

# Modo mapeado: cabecalhos reconhecidos (normalizados) -> chave interna do lead.
# Permite escrever em planilhas existentes com formato proprio (ex: abas da Laura
# 'Nome | Email | Telefone | Data Inscricao') respeitando a ordem DELAS.
_HEADER_MAP = {
    "nome": "name",
    "email": "email",
    "e-mail": "email",
    "telefone": "phone",
    "whatsapp": "phone",
    "fone": "phone",
    "data": "data_entrada_curta",
    "data inscricao": "data_entrada_curta",
    "data de inscricao": "data_entrada_curta",
    "data entrada": "data_entrada",
    "formulario": "flow_slug",
    "data agendamento": "scheduled_date",
    "hora agendamento": "scheduled_time",
    "utm source": "utm_source",
    "utm medium": "utm_medium",
    "utm campaign": "utm_campaign",
    "utm content": "utm_content",
    "utm term": "utm_term",
}


def _normalizar_header(h: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFD", (h or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class SheetsService:
    """Integracao com Google Sheets via service account — envia leads pra planilha."""

    def _get_client(self):
        json_str = settings.google_service_account_json
        if not json_str:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

        creds_info = json.loads(json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        return build("sheets", "v4", credentials=creds)

    @staticmethod
    def extract_sheet_id(sheet_url: str) -> Optional[str]:
        """Extrai o spreadsheetId de uma URL do Google Sheets."""
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", sheet_url or "")
        return match.group(1) if match else None

    def _resolve_tab(self, client, sheet_id: str, tab: Optional[str]) -> str:
        """Usa a aba informada ou a primeira aba da planilha."""
        if tab and tab.strip():
            return tab.strip()
        meta = client.spreadsheets().get(
            spreadsheetId=sheet_id, fields="sheets.properties.title"
        ).execute()
        sheets = meta.get("sheets", [])
        if not sheets:
            raise ValueError("Planilha sem abas")
        return sheets[0]["properties"]["title"]

    def _resolver_layout(self, client, sheet_id: str, tab: str) -> list[str]:
        """Resolve o layout de colunas da aba (lista de chaves internas, na ordem da aba).

        Regras:
        - Linha 1 vazia -> escreve o cabecalho padrao e retorna o layout padrao
        - TODOS os cabecalhos reconhecidos (padrao OU formato proprio tipo
          'Nome | Email | Telefone | Data') -> escreve na ordem DA ABA (modo mapeado)
        - Qualquer cabecalho desconhecido -> ValueError (nunca desalinha dados de terceiros)
        """
        res = client.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=f"'{tab}'!1:1"
        ).execute()
        values = res.get("values")
        if not values or not any(c.strip() for c in values[0]):
            client.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"'{tab}'!A1",
                body={"values": [HEADERS]},
                valueInputOption="RAW",
            ).execute()
            return [_HEADER_MAP[_normalizar_header(h)] for h in HEADERS]

        layout = []
        for h in values[0]:
            chave = _HEADER_MAP.get(_normalizar_header(h))
            if not chave:
                raise ValueError(
                    f"A aba '{tab}' tem a coluna desconhecida '{h}'. "
                    "Use uma aba vazia (o sistema cria as colunas), o padrao do Forms, "
                    "ou colunas simples reconhecidas (Nome, Email, Telefone, Data...)."
                )
            layout.append(chave)
        return layout

    @staticmethod
    def _format_date_br(date_str: str) -> str:
        """Converte YYYY-MM-DD pra DD/MM/YYYY (mantem como veio se nao bater)."""
        match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", (date_str or "").strip())
        return f"{match.group(3)}/{match.group(2)}/{match.group(1)}" if match else (date_str or "")

    @staticmethod
    def _build_row(layout: list[str], data: dict) -> list[str]:
        """Monta a linha na ordem do layout da aba (padrao ou mapeado)."""
        agora = datetime.now(TIMEZONE)
        valores = {
            "data_entrada": agora.strftime("%d/%m/%Y %H:%M"),
            "data_entrada_curta": agora.strftime("%d/%m/%Y"),
            "name": data.get("name") or "",
            "email": data.get("email") or "",
            "phone": data.get("phone") or "",
            "flow_slug": data.get("flow_slug") or "",
            "scheduled_date": SheetsService._format_date_br(data.get("scheduled_date") or ""),
            "scheduled_time": data.get("scheduled_time") or "",
            "utm_source": data.get("utm_source") or "",
            "utm_medium": data.get("utm_medium") or "",
            "utm_campaign": data.get("utm_campaign") or "",
            "utm_content": data.get("utm_content") or "",
            "utm_term": data.get("utm_term") or "",
        }
        return [valores.get(chave, "") for chave in layout]

    async def append_lead(self, sheet_url: str, tab: Optional[str], data: dict) -> dict:
        """Adiciona uma linha com o lead na planilha."""
        sheet_id = self.extract_sheet_id(sheet_url)
        if not sheet_id:
            return {"success": False, "error": "URL de planilha invalida"}

        try:
            client = self._get_client()
            tab_name = self._resolve_tab(client, sheet_id, tab)
            layout = self._resolver_layout(client, sheet_id, tab_name)

            client.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"'{tab_name}'!A1",
                body={"values": [self._build_row(layout, data)]},
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
            ).execute()

            logger.info(f"Sheets: lead {data.get('email')} adicionado na planilha {sheet_id} aba '{tab_name}'")
            return {"success": True}
        except Exception as e:
            logger.error(f"Sheets append error: {e}")
            return {"success": False, "error": str(e)}

    async def update_scheduling(
        self,
        sheet_url: str,
        tab: Optional[str],
        email: str,
        scheduled_date: str,
        scheduled_time: str,
        fallback_data: Optional[dict] = None,
    ) -> dict:
        """Preenche data/hora de agendamento na linha do lead (busca por email).

        Se o lead nao estiver na planilha, adiciona a linha completa (fallback).
        """
        sheet_id = self.extract_sheet_id(sheet_url)
        if not sheet_id:
            return {"success": False, "error": "URL de planilha invalida"}

        try:
            client = self._get_client()
            tab_name = self._resolve_tab(client, sheet_id, tab)
            layout = self._resolver_layout(client, sheet_id, tab_name)

            # Abas sem colunas de agendamento (ex: formato simples da Laura):
            # nada a atualizar — a entrada do lead ja foi registrada no append.
            if "scheduled_date" not in layout and "scheduled_time" not in layout:
                return {"success": True, "skipped": "aba sem colunas de agendamento"}

            if "email" not in layout:
                data = dict(fallback_data or {})
                data["email"] = email
                data["scheduled_date"] = scheduled_date
                data["scheduled_time"] = scheduled_time
                return await self.append_lead(sheet_url, tab, data)

            col_email = layout.index("email")
            res = client.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f"'{tab_name}'!A:{chr(65 + len(layout) - 1)}"
            ).execute()
            rows = res.get("values", [])

            # Busca de baixo pra cima a ultima linha com o email do lead
            target_row = None
            email_lower = (email or "").strip().lower()
            for i in range(len(rows) - 1, 0, -1):  # pula linha 1 (cabecalho)
                row = rows[i]
                if len(row) > col_email and row[col_email].strip().lower() == email_lower:
                    target_row = i + 1  # 1-indexed
                    break

            if target_row:
                updates = []
                if "scheduled_date" in layout:
                    col = chr(65 + layout.index("scheduled_date"))
                    updates.append({"range": f"'{tab_name}'!{col}{target_row}",
                                    "values": [[self._format_date_br(scheduled_date)]]})
                if "scheduled_time" in layout:
                    col = chr(65 + layout.index("scheduled_time"))
                    updates.append({"range": f"'{tab_name}'!{col}{target_row}",
                                    "values": [[scheduled_time]]})
                client.spreadsheets().values().batchUpdate(
                    spreadsheetId=sheet_id,
                    body={"valueInputOption": "RAW", "data": updates},
                ).execute()
                logger.info(f"Sheets: agendamento de {email} atualizado (linha {target_row})")
                return {"success": True, "updated_row": target_row}

            # Lead nao encontrado — adiciona linha completa
            data = dict(fallback_data or {})
            data["email"] = email
            data["scheduled_date"] = scheduled_date
            data["scheduled_time"] = scheduled_time
            return await self.append_lead(sheet_url, tab, data)
        except Exception as e:
            logger.error(f"Sheets update error: {e}")
            return {"success": False, "error": str(e)}
