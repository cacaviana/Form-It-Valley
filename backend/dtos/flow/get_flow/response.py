from pydantic import BaseModel, Field


class GetFlowResponse(BaseModel):
    id: str = Field(..., alias="_id")
    tenant_id: str
    name: str
    slug: str
    status: str
    version: int
    nodes: list[dict]
    edges: list[dict]
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
