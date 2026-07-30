from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScanCreate(BaseModel):
    scanner: str


class ScanRead(BaseModel):
    id: UUID
    asset_id: UUID
    scanner: str
    status: str
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True