from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScanResultRead(BaseModel):
    id: UUID
    scan_id: UUID
    asset_id: UUID
    port: int
    protocol: str
    state: str
    service: str | None
    product: str | None
    version: str | None
    hostname: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
