from pydantic import BaseModel, Field


class FlowSummary(BaseModel):
    id: str = Field(..., alias="_id")
    tenant_id: str
    name: str
    slug: str
    status: str
    version: int
    node_count: int
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True


class ListFlowsResponse(BaseModel):
    flows: list[FlowSummary]
    total: int
