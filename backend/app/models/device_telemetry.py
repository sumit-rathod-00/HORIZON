"""Device telemetry model for HORIZON."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class DeviceTelemetry(Base):
    """Represents telemetry data collected from a device."""

    __tablename__ = "device_telemetry"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Telemetry metadata
    telemetry_version: Mapped[str] = mapped_column(String(20), nullable=False)
    agent_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # System metrics
    cpu_usage_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    memory_total_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_used_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_usage_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    disk_total_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_used_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_usage_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Network information
    network_interfaces: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    active_connections: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Security state
    firewall_enabled: Mapped[bool | None] = mapped_column(nullable=True)
    antivirus_enabled: Mapped[bool | None] = mapped_column(nullable=True)
    os_updates_pending: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Additional metadata (using extra_data to avoid reserved 'metadata' name)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<DeviceTelemetry device={self.device_id} collected={self.collected_at}>"
