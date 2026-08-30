"""Device schemas for API requests and responses."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    """Schema for creating a new device."""
    name: str = Field(..., min_length=1, max_length=120)
    platform: str | None = Field(None, max_length=50)
    operating_system: str | None = Field(None, max_length=100)
    device_type: str | None = Field(None, max_length=50)


class DeviceUpdate(BaseModel):
    """Schema for updating device information."""
    name: str | None = Field(None, min_length=1, max_length=120)
    platform: str | None = Field(None, max_length=50)
    operating_system: str | None = Field(None, max_length=100)
    device_type: str | None = Field(None, max_length=50)
    status: str | None = None


class DeviceRead(BaseModel):
    """Schema for device response."""
    id: UUID
    owner_id: UUID
    name: str
    platform: str | None
    operating_system: str | None
    device_type: str | None
    status: str
    last_seen: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceEnrollResponse(BaseModel):
    """Schema for successful device enrollment response."""
    device: DeviceRead
    enrollment_token: str
    message: str
