from pydantic import BaseModel
from typing import Optional


class UploadBlacklistCsvResponse(BaseModel):
    blacklist_id: str
    total_entries: int
    skipped_lines: int
    errors: list[str] = []
    csv_uploaded_at: str
