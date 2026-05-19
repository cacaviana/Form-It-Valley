from pydantic import BaseModel
from typing import Optional


class CheckLeadResponse(BaseModel):
    blocked: bool
    matched_field: Optional[str] = None  # "email" | "phone" | None
