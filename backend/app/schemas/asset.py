from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    asset_type: str = Field(min_length=1, max_length=50)
    ip_address: str | None = Field(default=None, max_length=50)

    @field_validator("name", "asset_type")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be empty")
        return value


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    asset_type: str | None = Field(default=None, min_length=1, max_length=50)
    ip_address: str | None = Field(default=None, max_length=50)

    @field_validator("name", "asset_type")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Value must not be empty")
        return value


class AssetRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    asset_type: str
    ip_address: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
