from pydantic import BaseModel
from typing import Optional


class SubmissionSummary(BaseModel):
    id: str
    tenant_id: str
    flow_id: str
    flow_slug: str
    client_name: str
    client_email: str
    end_type: str
    status: str
    has_quote: bool
    created_at: str


class ListSubmissionsResponse(BaseModel):
    submissions: list[SubmissionSummary]
    total: int
