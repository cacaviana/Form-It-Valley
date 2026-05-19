from pydantic import BaseModel, Field
from typing import Optional


class CheckLeadRequest(BaseModel):
    flow_id: str = Field(..., min_length=1)
    email: Optional[str] = None
    ddi: Optional[str] = None
    ddd: Optional[str] = None
    numero: Optional[str] = None
    tenant_id: Optional[str] = Field(default="tenant_1")
