from fastapi import APIRouter
from pydantic import BaseModel
from config.database import mongodb_client

router = APIRouter(prefix="/api/scheduling-config", tags=["scheduling-config"])

CONFIG_ID = "scheduling_config"


class SchedulingConfigRequest(BaseModel):
    morning_slots: int = 3
    afternoon_slots: int = 3
    max_bookings_per_slot: int = 1


@router.get("")
async def get_config():
    """Retorna config de horarios disponiveis."""
    db = mongodb_client.database
    config = await db["settings"].find_one({"_id": CONFIG_ID})
    return {
        "morning_slots": config.get("morning_slots", 3) if config else 3,
        "afternoon_slots": config.get("afternoon_slots", 3) if config else 3,
        "max_bookings_per_slot": config.get("max_bookings_per_slot", 1) if config else 1,
    }


@router.put("")
async def update_config(request: SchedulingConfigRequest):
    """Atualiza config de horarios disponiveis."""
    from datetime import datetime, timezone

    max_bookings = max(1, request.max_bookings_per_slot)

    db = mongodb_client.database
    await db["settings"].update_one(
        {"_id": CONFIG_ID},
        {"$set": {
            "morning_slots": request.morning_slots,
            "afternoon_slots": request.afternoon_slots,
            "max_bookings_per_slot": max_bookings,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    return {
        "morning_slots": request.morning_slots,
        "afternoon_slots": request.afternoon_slots,
        "max_bookings_per_slot": max_bookings,
    }
