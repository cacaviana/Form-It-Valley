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

    def _ensure_headers(self, client, sheet_id: str, tab: str):
        """Escreve o cabecalho na linha 1 se vazio; recusa planilha com colunas diferentes.

        Regras:
        - Linha 1 vazia -> escreve o cabecalho padrao (planilha nova)
        - Linha 1 igual ao padrao (colunas extras a direita OK) -> segue normal
        - Linha 1 diferente -> ValueError (nunca desalinha dados de planilha existente)
        """
        res = client.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=f"'{tab}'!A1:L1"
        ).execute()
        values = res.get("values")
        if not values:
            client.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"'{tab}'!A1",
                body={"values": [HEADERS]},
                valueInputOption="RAW",
            ).execute()
            return

        existing = [c.strip().lower() for c in values[0]]
        expected = [c.lower() for c in HEADERS]
        if existing[: len(expected)] != expected:
            raise ValueError(
                f"A aba '{tab}' ja tem colunas diferentes do padrao. "
                "Use uma planilha/aba vazia (o sistema cria as colunas) ou uma ja no padrao do Forms."
            )

    @staticmethod
    def _format_date_br(date_str: str) -> str:
        """Converte YYYY-MM-DD pra DD/MM/YYYY (mantem como veio se nao bater)."""
        match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", (date_str or "").strip())
        return f"{match.group(3)}/{match.group(2)}/{match.group(1)}" if match else (date_str or "")

    @staticmethod
    def _build_row(data: dict) -> list[str]:
        agora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M")
        return [
            agora,
            data.get("name") or "",
            data.get("email") or "",
            data.get("phone") or "",
            data.get("flow_slug") or "",
            SheetsService._format_date_br(data.get("scheduled_date") or ""),
            data.get("scheduled_time") or "",
            data.get("utm_source") or "",
            data.get("utm_medium") or "",
            data.get("utm_campaign") or "",
            data.get("utm_content") or "",
            data.get("utm_term") or "",
        ]

    async def append_lead(self, sheet_url: str, tab: Optional[str], data: dict) -> dict:
        """Adiciona uma linha com o lead na planilha."""
        sheet_id = self.extract_sheet_id(sheet_url)
        if not sheet_id:
            return {"success": False, "error": "URL de planilha invalida"}

        try:
            client = self._get_client()
            tab_name = self._resolve_tab(client, sheet_id, tab)
            self._ensure_headers(client, sheet_id, tab_name)

            client.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"'{tab_name}'!A1",
                body={"values": [self._build_row(data)]},
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
            ).execute()

            logger.info(f"Sheets: lead {data.get('email')} adicionado na planilha {sheet_id}")
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
            self._ensure_headers(client, sheet_id, tab_name)

            res = client.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f"'{tab_name}'!A:L"
            ).execute()
            rows = res.get("values", [])

            # Busca de baixo pra cima a ultima linha com o email do lead
            target_row = None
            email_lower = (email or "").strip().lower()
            for i in range(len(rows) - 1, 0, -1):  # pula linha 1 (cabecalho)
                row = rows[i]
                if len(row) > COL_EMAIL and row[COL_EMAIL].strip().lower() == email_lower:
                    target_row = i + 1  # 1-indexed
                    break

            if target_row:
                client.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=f"'{tab_name}'!{COL_DATA_AGENDAMENTO}{target_row}:{COL_HORA_AGENDAMENTO}{target_row}",
                    body={"values": [[self._format_date_br(scheduled_date), scheduled_time]]},
                    valueInputOption="RAW",
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
