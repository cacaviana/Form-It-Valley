from pydantic import BaseModel
from typing import Optional


class QuoteItemResponse(BaseModel):
    description: str
    unit_price: float
    quantity: int
    subtotal: float


class QuoteDataResponse(BaseModel):
    items: list[QuoteItemResponse]
    subtotal: float
    taxes_tps: float
    taxes_tvq: float
    total: float
    recommendations: str = ""
    notes: str = ""


class CreateSubmissionResponse(BaseModel):
    id: str
    tenant_id: str
    flow_id: str
    flow_slug: str
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    client_address: Optional[str] = None
    answers: list[dict]
    end_node_id: str
    end_type: str
    quote_text: Optional[str] = None
    quote_data: Optional[QuoteDataResponse] = None
    status: str
    created_at: str
