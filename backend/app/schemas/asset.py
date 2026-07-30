from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    name: str
    asset_type: str
    ip_address: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    ip_address: str | None = None


class AssetRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    asset_type: str
    ip_address: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)