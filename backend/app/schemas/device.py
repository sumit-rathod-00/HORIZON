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


class DeviceHeartbeatRequest(BaseModel):
    """Schema for device heartbeat request from agent."""
    device_id: UUID | None = None
    enrollment_token: str
    agent_version: str = Field(..., max_length=50)
    timestamp: datetime
    status: str = Field(default="healthy", max_length=20)


class DeviceHeartbeatResponse(BaseModel):
    """Schema for heartbeat response to agent."""
    device_id: UUID
    status: str
    heartbeat_interval_seconds: int
    telemetry_enabled: bool
    message: str | None = None


class TelemetryIngest(BaseModel):
    """Schema for telemetry ingestion request."""
    telemetry_version: str = Field(default="1.0", max_length=20)
    agent_version: str | None = Field(None, max_length=50)
    collected_at: datetime | None = None

    # System metrics
    cpu_usage_percent: float | None = Field(None, ge=0, le=100)
    memory_total_mb: int | None = Field(None, ge=0)
    memory_used_mb: int | None = Field(None, ge=0)
    memory_usage_percent: float | None = Field(None, ge=0, le=100)
    disk_total_gb: int | None = Field(None, ge=0)
    disk_used_gb: int | None = Field(None, ge=0)
    disk_usage_percent: float | None = Field(None, ge=0, le=100)

    # Network
    network_interfaces: list[dict] | None = None
    active_connections: int | None = Field(None, ge=0)

    # Security state
    firewall_enabled: bool | None = None
    antivirus_enabled: bool | None = None
    os_updates_pending: int | None = Field(None, ge=0)

    # Extra data
    extra_data: dict | None = None


class TelemetryResponse(BaseModel):
    """Schema for telemetry ingestion response."""
    telemetry_id: UUID
    status: str = "accepted"
    received_at: datetime
