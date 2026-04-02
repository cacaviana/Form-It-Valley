from pydantic import BaseModel, Field
from typing import Optional


class SaveFlowRequest(BaseModel):
    name: str = Field(..., min_length=1)
    slug: Optional[str] = None
    nodes: list[dict] = Field(..., min_length=1)
    edges: list[dict] = Field(default=[])
    status: Optional[str] = Field(default="draft")
    tenant_id: Optional[str] = Field(default="tenant_1")
    pricing_csv: Optional[str] = Field(default=None)
    activecampaign_list_id: Optional[str] = Field(default=None)
    activecampaign_list_name: Optional[str] = Field(default=None)
    theme_color: Optional[str] = Field(default="violet")
