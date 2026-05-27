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

        delegate_email = settings.google_delegate_email
        if delegate_email:
            creds = creds.with_subject(delegate_email)

        return build("calendar", "v3", credentials=creds)

    def _get_calendar_id(self) -> str:
        return settings.google_calendar_id or "primary"

    async def _resolve_calendar_id(self, flow_id: Optional[str]) -> str:
        """Agenda do flow tem prioridade; senao cai pra global."""
        if flow_id:
            try:
                from data.repositories.mongo.flow_repository import FlowRepository
                flow_doc = await FlowRepository().find_by_id(flow_id)
                if flow_doc:
                    cal = flow_doc.get("gcal_calendar_id")
                    if isinstance(cal, str) and cal.strip():
                        return cal.strip()
            except Exception:
                pass
        return self._get_calendar_id()

    def _sync_list_calendars(self) -> list:
        calendar = self._get_calendar_client()
        # showHidden=True pra incluir agendas compartilhadas que estao "ocultas" na lista da SA
        res = calendar.calendarList().list(showHidden=True).execute()
        return res.get("items", [])

    def _sync_subscribe_calendar(self, calendar_id: str) -> dict:
        """Adiciona uma agenda na calendarList da SA pra que apareca em list_calendars."""
        calendar = self._get_calendar_client()
        return calendar.calendarList().insert(body={"id": calendar_id}).execute()

    async def subscribe_to_calendar(self, calendar_id: str) -> bool:
        """Garante que uma agenda esta na lista da SA (necessario pra ela aparecer em list_calendars).

        Se a SA ja tem acesso (foi compartilhada) mas a agenda nao apareceu automaticamente
        na calendarList, chamar isso adiciona explicitamente. Idempotente — se ja esta, retorna ok.
        """
        if not calendar_id:
            return False
        try:
            await asyncio.to_thread(self._sync_subscribe_calendar, calendar_id)
            return True
        except Exception as e:
            # 409 Conflict = ja esta na lista (ok). Outros erros = problema (sem acesso, etc)
            err_str = str(e)
            if "409" in err_str or "duplicate" in err_str.lower():
                return True
            logger.warning(f"GCal subscribe_to_calendar ({calendar_id}) error: {e}")
            return False

    async def list_calendars(self) -> list[dict]:
        """Lista agendas acessiveis pela service account."""
        try:
            items = await asyncio.to_thread(self._sync_list_calendars)
            return [{
                "id": c.get("id", ""),
                "summary": c.get("summary", ""),
                "primary": bool(c.get("primary", False)),
                "access_role": c.get("accessRole", "")
            } for c in items if c.get("id")]
        except Exception as e:
            logger.error(f"GCal list_calendars error: {e}")
            return []

    async def _get_global_config(self) -> tuple[int, int, int]:
        """Retorna config global (morning_slots, afternoon_slots, max_bookings_per_slot)."""
        try:
            db = mongodb_client.database
            config = await db["settings"].find_one({"_id": "scheduling_config"})
            if config:
                return (
                    config.get("morning_slots", 3),
                    config.get("afternoon_slots", 3),
                    max(1, config.get("max_bookings_per_slot", 1)),
                )
        except Exception:
            pass
        return 3, 3, 1

    async def _get_flow_custom_config(self, flow_id: Optional[str]) -> Optional[dict]:
        """Retorna config personalizada do flow no novo schema, se existir e for válida.

        Schema esperado:
          { "dates": [{"date": "YYYY-MM-DD", "times": ["HH:MM", ...]}, ...],
            "max_bookings_per_slot": int }
        """
        if not flow_id:
            return None
        try:
            from data.repositories.mongo.flow_repository import FlowRepository
            flow_doc = await FlowRepository().find_by_id(flow_id)
            if not flow_doc:
                return None
            cfg = flow_doc.get("scheduling_config")
            if not isinstance(cfg, dict):
                return None
            if not isinstance(cfg.get("dates"), list):
                return None
            # Indexar por data pra acesso O(1)
            date_map: dict[str, list[str]] = {}
            for entry in cfg["dates"]:
                if not isinstance(entry, dict):
                    continue
                date = entry.get("date")
                times = entry.get("times")
                if isinstance(date, str) and isinstance(times, list):
                    date_map[date] = [t for t in times if isinstance(t, str)]
            return {
                "date_map": date_map,
                "max_bookings_per_slot": max(1, int(cfg.get("max_bookings_per_slot", 1))),
            }
        except Exception:
            return None

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

    async def get_available_dates(self, month: int, year: int, flow_id: Optional[str] = None) -> list[dict]:
        """Retorna dias do mes com disponibilidade.

        Se o flow tiver config personalizada (lista de datas + horarios), so as datas listadas
        ficam disponiveis (filtradas por bookings do GCal). Senao, modo global.
        """
        days_in_month = cal_mod.monthrange(year, month)[1]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        flow_cfg = await self._get_flow_custom_config(flow_id)

        # Buscar eventos do mes (em ambos os modos, pra calcular bookings)
        events_per_day: dict[str, int] = {}
        try:
            cal_id = await self._resolve_calendar_id(flow_id)
            start_date = f"{year}-{str(month).zfill(2)}-01T00:00:00-03:00"
            end_date = f"{year}-{str(month).zfill(2)}-{days_in_month}T23:59:59-03:00"
            events = await asyncio.to_thread(self._sync_list_events, cal_id, start_date, end_date)
            for event in events:
                start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
                if start:
                    day_str = start[:10]
                    events_per_day[day_str] = events_per_day.get(day_str, 0) + 1
        except Exception as e:
            logger.error(f"GCal get_available_dates error: {e}")
            # Continua sem dados de eventos — assume todos vazios

        # ── MODO PERSONALIZADO (lista de datas) ──
        if flow_cfg is not None:
            date_map: dict[str, list[str]] = flow_cfg["date_map"]
            max_bookings: int = flow_cfg["max_bookings_per_slot"]
            dates = []
            for day in range(1, days_in_month + 1):
                d = datetime(year, month, day)
                date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
                is_future = d >= today
                configured_times = date_map.get(date_str, [])
                if not configured_times or not is_future:
                    dates.append({"date": date_str, "available": False, "slots_count": 0})
                    continue
                # Capacidade = qtd horarios configurados * max_bookings; ocupado = events_per_day
                capacity = len(configured_times) * max_bookings
                free = max(0, capacity - events_per_day.get(date_str, 0))
                dates.append({
                    "date": date_str,
                    "available": free > 0,
                    "slots_count": min(free, len(configured_times)),
                })
            return dates

        # ── MODO GLOBAL (comportamento original) ──
        morning_limit, afternoon_limit, max_bookings = await self._get_global_config()
        max_slots = morning_limit + afternoon_limit
        total_capacity = ALL_SLOTS_COUNT * max_bookings

        dates = []
        for day in range(1, days_in_month + 1):
            d = datetime(year, month, day)
            date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
            is_weekday = d.weekday() < 5
            is_future = d >= today
            day_events = events_per_day.get(date_str, 0)
            real_free = max(0, total_capacity - day_events)
            visible_slots = min(real_free, max_slots)
            dates.append({
                "date": date_str,
                "available": is_weekday and is_future and real_free > 0,
                "slots_count": visible_slots if (is_weekday and is_future) else 0,
            })
        return dates

    async def get_available_slots(self, date_str: str, flow_id: Optional[str] = None) -> list[str]:
        """Retorna horarios disponiveis para uma data.

        Modo personalizado (flow tem config de datas) -> usa lista exata do flow.
        Modo global -> usa MORNING_SLOTS + AFTERNOON_SLOTS com limites do slider.
        """
        flow_cfg = await self._get_flow_custom_config(flow_id)
        try:
            cal_id = await self._resolve_calendar_id(flow_id)
            events = await asyncio.to_thread(
                self._sync_list_events, cal_id,
                f"{date_str}T00:00:00-03:00",
                f"{date_str}T23:59:59-03:00",
            )

            busy_counts: dict[str, int] = {}
            for event in events:
                start = event.get("start", {}).get("dateTime")
                if start:
                    try:
                        start_dt = datetime.fromisoformat(start)
                        hm = start_dt.strftime("%H:%M")
                        busy_counts[hm] = busy_counts.get(hm, 0) + 1
                    except ValueError:
                        pass

            # Filtro de horarios passados (se a data for hoje)
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo("America/Sao_Paulo"))
            is_today = date_str == now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M") if is_today else ""

            # ── MODO PERSONALIZADO ──
            if flow_cfg is not None:
                date_map: dict[str, list[str]] = flow_cfg["date_map"]
                max_bookings: int = flow_cfg["max_bookings_per_slot"]
                configured = date_map.get(date_str, [])
                # Aceita so os horarios configurados e nao saturados; ordena
                available = sorted([
                    t for t in configured
                    if busy_counts.get(t, 0) < max_bookings and (not is_today or t > current_time)
                ])
                return available

            # ── MODO GLOBAL (logica original) ──
            morning_limit, afternoon_limit, max_bookings = await self._get_global_config()

            # Constroi lista de busy ranges pra checar overlap em slots de 30min
            busy_ranges: list[dict[str, str]] = []
            for event in events:
                start = event.get("start", {}).get("dateTime")
                end = event.get("end", {}).get("dateTime")
                if start and end:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                    busy_ranges.append({"start": start_dt.strftime("%H:%M"), "end": end_dt.strftime("%H:%M")})

            available = []
            for slot in ALL_SLOTS:
                h, m = int(slot[:2]), int(slot[3:])
                end_h = h + (1 if m + 30 >= 60 else 0)
                end_m = (m + 30) % 60
                slot_end = f"{str(end_h).zfill(2)}:{str(end_m).zfill(2)}"

                overlap_count = sum(
                    1 for b in busy_ranges if slot < b["end"] and slot_end > b["start"]
                )
                if overlap_count < max_bookings:
                    available.append(slot)

            if is_today:
                available = [s for s in available if s > current_time]

            return self._apply_slots_limit(available, morning_limit, afternoon_limit)

        except Exception as e:
            logger.error(f"GCal get_available_slots error: {e}")
            # Fallback: se flow personalizado, devolve a lista bruta do flow; senao usa global default
            if flow_cfg is not None:
                return sorted(flow_cfg["date_map"].get(date_str, []))
            morning_limit, afternoon_limit = 3, 3
            return self._apply_slots_limit(ALL_SLOTS, morning_limit, afternoon_limit)

    async def create_event(
        self,
        lead_name: str,
        lead_email: str,
        lead_phone: str,
        scheduled_date: str,
        scheduled_time: str,
        event_title: Optional[str] = None,
        flow_id: Optional[str] = None,
    ) -> Optional[dict]:
        """Cria evento no Google Calendar. Retorna {event_id, html_link}.

        event_title aceita placeholders: {{nome}}, {{data}}, {{horario}}.
        flow_id usado pra resolver agenda customizada (gcal_calendar_id) e config personalizada.
        """
        try:
            cal_id = await self._resolve_calendar_id(flow_id)

            h, m = int(scheduled_time[:2]), int(scheduled_time[3:])
            end_h = h + (1 if m + 30 >= 60 else 0)
            end_m = (m + 30) % 60
            end_time = f"{str(end_h).zfill(2)}:{str(end_m).zfill(2)}"

            # Titulo do evento — texto fixo definido no flow ou default
            if event_title and event_title.strip():
                resolved_title = event_title.strip()
            else:
                resolved_title = "Call Consultor IT Valley"

            import uuid
            # Criamos o evento SEM attendees pra evitar erro com SA externa (Workspace bloqueia).
            # O convite oficial nao chega no lead — em vez disso, o email do Resend (no-reply) leva
            # um .ics anexado que o lead pode adicionar manualmente.
            event = {
                "summary": resolved_title,
                "description": f"Lead: {lead_name}\nEmail: {lead_email}\nTelefone: {lead_phone or 'N/A'}\n\nAgendado via FormItValley",
                "start": {
                    "dateTime": f"{scheduled_date}T{scheduled_time}:00",
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": f"{scheduled_date}T{end_time}:00",
                    "timeZone": "America/Sao_Paulo",
                },
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

            # Tenta com Meet; se falhar (agenda nao suporta), cria sem Meet
            meet_link = ""
            try:
                res = await asyncio.to_thread(self._sync_create_event_with_meet, cal_id, event)
            except Exception as err1:
                logger.warning(f"Meet nao suportado nessa agenda, criando sem: {err1}")
                event.pop("conferenceData", None)
                res = await asyncio.to_thread(self._sync_create_event, cal_id, event)

            conference = res.get("conferenceData", {})
            for ep in conference.get("entryPoints", []):
                if ep.get("entryPointType") == "video":
                    meet_link = ep.get("uri", "")
                    break

            logger.info(f"GCal evento criado: {res.get('id')} — Meet: {meet_link or 'N/A'}")
            return {
                "event_id": res.get("id", ""),
                "html_link": res.get("htmlLink", ""),
                "meet_link": meet_link,
            }

        except Exception as e:
            logger.error(f"GCal create_event error: {e}")
            return None
