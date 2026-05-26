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
    page_template: Optional[str] = Field(default="centered")
    page_content: Optional[dict] = Field(default=None)
    scheduling_config: Optional[dict] = Field(default=None)
    meeting_link_override: Optional[str] = Field(default=None)
    gcal_event_title: Optional[str] = Field(default=None)
    email_config: Optional[dict] = Field(default=None)
    ui_texts: Optional[dict] = Field(default=None)
