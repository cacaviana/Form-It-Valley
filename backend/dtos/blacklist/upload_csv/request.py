from pydantic import BaseModel, Field
from typing import Optional


class UploadBlacklistCsvRequest(BaseModel):
    csv_text: str = Field(..., min_length=1, description="Conteudo do CSV (header obrigatorio: email,ddi,ddd,numero)")
    scope_type: str = Field(default="flow", description="Escopo da blacklist: 'flow' (por formulario) ou 'tenant' (global)")
    scope_id: str = Field(..., min_length=1, description="ID do flow ou tenant a que esta blacklist pertence")
