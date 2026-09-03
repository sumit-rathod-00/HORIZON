"""Detection engine for identifying security events."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.device_telemetry import DeviceTelemetry
from app.repositories.device_telemetry_repository import DeviceTelemetryRepository
from app.services.security_event_service import SecurityEventService


class DetectionEngine:
    """Engine for detecting security-relevant changes and generating events."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._telemetry_repository = DeviceTelemetryRepository(session)
        self._event_service = SecurityEventService(session)

    async def detect_state_change(
        self,
        device: Device,
        old_status: str,
        new_status: str,
    ) -> None:
        """Detect and create event for device state change."""
        if old_status == new_status:
            return

        # Device went offline
        if old_status == "active" and new_status == "inactive":
            await self._event_service.create_event(
                device_id=device.id,
                event_type="device.inactive",
                severity="medium",
                title=f"Device {device.name} became inactive",
                description="Device has not sent heartbeat within expected timeout period",
                evidence={
                    "old_status": old_status,
                    "new_status": new_status,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                },
                detection_source="device_state_engine",
            )

        # Device came online
        elif old_status in ("pending", "inactive") and new_status == "active":
            await self._event_service.create_event(
                device_id=device.id,
                event_type="device.active",
                severity="info",
                title=f"Device {device.name} became active",
                description="Device is now sending heartbeats",
                evidence={
                    "old_status": old_status,
                    "new_status": new_status,
                },
                detection_source="device_state_engine",
            )

    async def detect_telemetry_changes(
        self,
        device: Device,
        current_telemetry: DeviceTelemetry,
    ) -> None:
        """Detect security-relevant changes in telemetry."""
        # Get previous telemetry
        telemetry_list = await self._telemetry_repository.get_by_device(device.id, limit=2)

        if len(telemetry_list) < 2:
            return  # No previous telemetry to compare

        previous_telemetry = telemetry_list[1]

        # Check firewall disabled
        if previous_telemetry.firewall_enabled and not current_telemetry.firewall_enabled:
            await self._event_service.create_event(
                device_id=device.id,
                event_type="security.firewall_disabled",
                severity="high",
                title=f"Firewall disabled on {device.name}",
                description="Device firewall was disabled",
                evidence={
                    "previous_state": True,
                    "current_state": False,
                    "detected_at": current_telemetry.collected_at.isoformat(),
                },
                detection_source="detection_engine",
            )

        # Check antivirus disabled
        if previous_telemetry.antivirus_enabled and not current_telemetry.antivirus_enabled:
            await self._event_service.create_event(
                device_id=device.id,
                event_type="security.antivirus_disabled",
                severity="high",
                title=f"Antivirus disabled on {device.name}",
                description="Device antivirus protection was disabled",
                evidence={
                    "previous_state": True,
                    "current_state": False,
                    "detected_at": current_telemetry.collected_at.isoformat(),
                },
                detection_source="detection_engine",
            )

        # Check disk usage critical
        if current_telemetry.disk_usage_percent and current_telemetry.disk_usage_percent > 90:
            if not previous_telemetry.disk_usage_percent or previous_telemetry.disk_usage_percent <= 90:
                await self._event_service.create_event(
                    device_id=device.id,
                    event_type="health.disk_critical",
                    severity="medium",
                    title=f"Disk usage critical on {device.name}",
                    description=f"Disk usage is at {current_telemetry.disk_usage_percent:.1f}%",
                    evidence={
                        "disk_usage_percent": current_telemetry.disk_usage_percent,
                        "disk_used_gb": current_telemetry.disk_used_gb,
                        "disk_total_gb": current_telemetry.disk_total_gb,
                    },
                    detection_source="detection_engine",
                )

        # Check OS updates increased significantly
        if current_telemetry.os_updates_pending and previous_telemetry.os_updates_pending:
            if current_telemetry.os_updates_pending > previous_telemetry.os_updates_pending + 5:
                await self._event_service.create_event(
                    device_id=device.id,
                    event_type="health.updates_pending",
                    severity="low",
                    title=f"OS updates pending on {device.name}",
                    description=f"{current_telemetry.os_updates_pending} OS updates are pending installation",
                    evidence={
                        "os_updates_pending": current_telemetry.os_updates_pending,
                        "previous_pending": previous_telemetry.os_updates_pending,
                    },
                    detection_source="detection_engine",
                )
