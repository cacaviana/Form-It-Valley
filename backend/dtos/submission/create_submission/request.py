from pydantic import BaseModel, Field
from typing import Optional


class SubmissionAnswer(BaseModel):
    node_id: str
    question: str
    value: str
    label: Optional[str] = None


class CreateSubmissionRequest(BaseModel):
    flow_id: str = Field(..., min_length=1)
    flow_slug: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    client_email: str = Field(..., min_length=1)
    client_phone: Optional[str] = None
    client_address: Optional[str] = None
    answers: list[SubmissionAnswer] = Field(..., min_length=1)
    end_node_id: str = Field(..., min_length=1)
    tenant_id: Optional[str] = Field(default="tenant_1")
