import asyncio
import calendar as cal_mod
import json
import logging
from datetime import datetime
from typing import Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.settings import settings
from config.database import mongodb_client

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

MORNING_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
AFTERNOON_SLOTS = ["14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
ALL_SLOTS = MORNING_SLOTS + AFTERNOON_SLOTS
ALL_SLOTS_COUNT = len(ALL_SLOTS)


class GCalService:
    """Integracao com Google Calendar via service account."""

    def _get_calendar_client(self):
        json_str = settings.google_service_account_json
        if not json_str:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

        creds_info = json.loads(json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

        return build("calendar", "v3", credentials=creds)

    def _get_calendar_id(self) -> str:
        return settings.google_calendar_id or "primary"

    async def _get_slots_config(self) -> tuple[int, int]:
        """Retorna (morning_slots, afternoon_slots) da config no MongoDB."""
        try:
            db = mongodb_client.database
            config = await db["settings"].find_one({"_id": "scheduling_config"})
            if config:
                return config.get("morning_slots", 3), config.get("afternoon_slots", 3)
        except Exception:
            pass
        return 3, 3

    def _apply_slots_limit(self, available: list[str], morning_limit: int, afternoon_limit: int) -> list[str]:
        """Limita horarios disponiveis conforme config, escolhendo aleatoriamente."""
        import random
        morning = [s for s in available if s < "12:00"]
        afternoon = [s for s in available if s >= "12:00"]
        if len(morning) > morning_limit:
            morning = sorted(random.sample(morning, morning_limit))
        if len(afternoon) > afternoon_limit:
            afternoon = sorted(random.sample(afternoon, afternoon_limit))
        return morning + afternoon

    # ─── Metodos sincronos (rodam em thread) ───

    def _sync_list_events(self, cal_id: str, time_min: str, time_max: str) -> list:
        calendar = self._get_calendar_client()
        res = calendar.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
            timeZone="America/Sao_Paulo",
        ).execute()
        return res.get("items", [])

    def _sync_create_event(self, cal_id: str, event: dict) -> dict:
        calendar = self._get_calendar_client()
        return calendar.events().insert(
            calendarId=cal_id,
            body=event,
            sendUpdates="all",
        ).execute()

    def _sync_create_event_with_meet(self, cal_id: str, event: dict) -> dict:
        calendar = self._get_calendar_client()
        return calendar.events().insert(
            calendarId=cal_id,
            body=event,
            conferenceDataVersion=1,
            sendUpdates="all",
        ).execute()

    # ─── Metodos async (wrappers) ───

    async def get_available_dates(self, month: int, year: int) -> list[dict]:
        """Retorna dias do mes com disponibilidade."""
        days_in_month = cal_mod.monthrange(year, month)[1]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        morning_limit, afternoon_limit = await self._get_slots_config()
        max_slots = morning_limit + afternoon_limit

        try:
            cal_id = self._get_calendar_id()
            start_date = f"{year}-{str(month).zfill(2)}-01T00:00:00-03:00"
            end_date = f"{year}-{str(month).zfill(2)}-{days_in_month}T23:59:59-03:00"

            events = await asyncio.to_thread(self._sync_list_events, cal_id, start_date, end_date)

            events_per_day: dict[str, int] = {}
            for event in events:
                start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
                if start:
                    day_str = start[:10]
                    events_per_day[day_str] = events_per_day.get(day_str, 0) + 1

            dates = []
            for day in range(1, days_in_month + 1):
                d = datetime(year, month, day)
                date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
                is_weekday = d.weekday() < 5
                is_future = d >= today
                day_events = events_per_day.get(date_str, 0)
                real_free = max(0, ALL_SLOTS_COUNT - day_events)
                visible_slots = min(real_free, max_slots)

                dates.append({
                    "date": date_str,
                    "available": is_weekday and is_future and real_free > 0,
                    "slots_count": visible_slots if (is_weekday and is_future) else 0,
                })
            return dates

        except Exception as e:
            logger.error(f"GCal get_available_dates error: {e}")
            dates = []
            for day in range(1, days_in_month + 1):
                d = datetime(year, month, day)
                date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
                is_weekday = d.weekday() < 5
                is_future = d >= today
                dates.append({
                    "date": date_str,
                    "available": is_weekday and is_future,
                    "slots_count": min(ALL_SLOTS_COUNT, max_slots) if (is_weekday and is_future) else 0,
                })
            return dates

    async def get_available_slots(self, date_str: str) -> list[str]:
        """Retorna horarios disponiveis para uma data, limitados pela config."""
        try:
            cal_id = self._get_calendar_id()
            morning_limit, afternoon_limit = await self._get_slots_config()

            events = await asyncio.to_thread(
                self._sync_list_events, cal_id,
                f"{date_str}T00:00:00-03:00",
                f"{date_str}T23:59:59-03:00",
            )

            busy: list[dict[str, str]] = []
            for event in events:
                start = event.get("start", {}).get("dateTime")
                end = event.get("end", {}).get("dateTime")
                if start and end:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                    busy.append({"start": start_dt.strftime("%H:%M"), "end": end_dt.strftime("%H:%M")})

            available = []
            for slot in ALL_SLOTS:
                h, m = int(slot[:2]), int(slot[3:])
                end_h = h + (1 if m + 30 >= 60 else 0)
                end_m = (m + 30) % 60
                slot_end = f"{str(end_h).zfill(2)}:{str(end_m).zfill(2)}"

                is_free = True
                for b in busy:
                    if slot < b["end"] and slot_end > b["start"]:
                        is_free = False
                        break
                if is_free:
                    available.append(slot)

            return self._apply_slots_limit(available, morning_limit, afternoon_limit)

        except Exception as e:
            logger.error(f"GCal get_available_slots error: {e}")
            morning_limit, afternoon_limit = 3, 3
            return self._apply_slots_limit(ALL_SLOTS, morning_limit, afternoon_limit)

    async def create_event(
        self,
        lead_name: str,
        lead_email: str,
        lead_phone: str,
        scheduled_date: str,
        scheduled_time: str,
    ) -> Optional[dict]:
        """Cria evento no Google Calendar. Retorna {event_id, html_link}."""
        try:
            cal_id = self._get_calendar_id()

            h, m = int(scheduled_time[:2]), int(scheduled_time[3:])
            end_h = h + (1 if m + 30 >= 60 else 0)
            end_m = (m + 30) % 60
            end_time = f"{str(end_h).zfill(2)}:{str(end_m).zfill(2)}"

            import uuid
            event = {
                "summary": f"Call Vendas - {lead_name}",
                "description": f"Lead: {lead_name}\nEmail: {lead_email}\nTelefone: {lead_phone or 'N/A'}\n\nAgendado via FormItValley",
                "start": {
                    "dateTime": f"{scheduled_date}T{scheduled_time}:00",
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": f"{scheduled_date}T{end_time}:00",
                    "timeZone": "America/Sao_Paulo",
                },
                "attendees": [
                    {"email": lead_email},
                ],
                "conferenceData": {
                    "createRequest": {
                        "requestId": str(uuid.uuid4()),
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [{"method": "popup", "minutes": 30}],
                },
            }

            # Tentar criar com Meet
            meet_link = ""
            try:
                res = await asyncio.to_thread(self._sync_create_event_with_meet, cal_id, event)
                conference = res.get("conferenceData", {})
                for ep in conference.get("entryPoints", []):
                    if ep.get("entryPointType") == "video":
                        meet_link = ep.get("uri", "")
                        break
            except Exception as meet_err:
                # Calendario nao suporta Meet — criar sem conferenceData
                logger.warning(f"Meet nao suportado, criando sem: {meet_err}")
                event.pop("conferenceData", None)
                res = await asyncio.to_thread(self._sync_create_event, cal_id, event)

            logger.info(f"GCal evento criado: {res.get('id')} — Meet: {meet_link or 'N/A'}")
            return {
                "event_id": res.get("id", ""),
                "html_link": res.get("htmlLink", ""),
                "meet_link": meet_link,
            }

        except Exception as e:
            logger.error(f"GCal create_event error: {e}")
            return None
