from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    scanner: str


class ScanStatusUpdate(BaseModel):
    status: str


class ScanRead(BaseModel):
    id: UUID
    asset_id: UUID
    scanner: str
    status: str
    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)