"""Telemetry ingestion service."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, BadRequestException, DeviceNotFoundException
from app.models.device import Device
from app.models.device_telemetry import DeviceTelemetry
from app.repositories.device_repository import DeviceRepository
from app.repositories.device_telemetry_repository import DeviceTelemetryRepository
from app.services.detection_engine import DetectionEngine


class TelemetryService:
    """Service for ingesting and managing device telemetry."""

    MAX_PAYLOAD_SIZE_MB = 1
    TELEMETRY_CURRENT_VERSION = "1.0"

    def __init__(self, session: AsyncSession):
        self._session = session
        self._device_repository = DeviceRepository(session)
        self._telemetry_repository = DeviceTelemetryRepository(session)

    async def ingest_telemetry(
        self,
        device_id: UUID,
        enrollment_token: str,
        telemetry_data: dict,
    ) -> DeviceTelemetry:
        """
        Ingest telemetry from a device.

        Validates authentication, validates payload, and stores telemetry.
        """
        # Authenticate device
        device = await self._authenticate_device(device_id, enrollment_token)

        # Validate telemetry schema
        self._validate_telemetry(telemetry_data)

        # Create telemetry record
        telemetry = DeviceTelemetry(
            device_id=device.id,
            telemetry_version=telemetry_data.get("telemetry_version", self.TELEMETRY_CURRENT_VERSION),
            agent_version=telemetry_data.get("agent_version"),
            cpu_usage_percent=telemetry_data.get("cpu_usage_percent"),
            memory_total_mb=telemetry_data.get("memory_total_mb"),
            memory_used_mb=telemetry_data.get("memory_used_mb"),
            memory_usage_percent=telemetry_data.get("memory_usage_percent"),
            disk_total_gb=telemetry_data.get("disk_total_gb"),
            disk_used_gb=telemetry_data.get("disk_used_gb"),
            disk_usage_percent=telemetry_data.get("disk_usage_percent"),
            network_interfaces=telemetry_data.get("network_interfaces"),
            active_connections=telemetry_data.get("active_connections"),
            firewall_enabled=telemetry_data.get("firewall_enabled"),
            antivirus_enabled=telemetry_data.get("antivirus_enabled"),
            os_updates_pending=telemetry_data.get("os_updates_pending"),
            extra_data=telemetry_data.get("extra_data"),
            collected_at=telemetry_data.get("collected_at", datetime.now(timezone.utc)),
            received_at=datetime.now(timezone.utc),
        )

        created = await self._telemetry_repository.create(telemetry)
        await self._session.commit()

        # Run detection engine on new telemetry
        detection_engine = DetectionEngine(self._session)
        await detection_engine.detect_telemetry_changes(device, created)

        return created

    async def _authenticate_device(
        self,
        device_id: UUID,
        enrollment_token: str,
    ) -> Device:
        """Authenticate device using enrollment token."""
        if not enrollment_token:
            raise UnauthorizedException("Enrollment token required")

        device = await self._device_repository.get_by_id(device_id)
        if device is None:
            raise DeviceNotFoundException()

        if device.status == "revoked":
            raise UnauthorizedException("Device has been revoked")

        if not device.enrollment_token_hash:
            raise UnauthorizedException("Device enrollment token not configured")

        if not bcrypt.verify(enrollment_token, device.enrollment_token_hash):
            raise UnauthorizedException("Invalid enrollment token")

        return device

    def _validate_telemetry(self, telemetry_data: dict) -> None:
        """Validate telemetry payload."""
        if not isinstance(telemetry_data, dict):
            raise BadRequestException("Telemetry must be a JSON object")

        # Validate collected_at timestamp if present
        if "collected_at" in telemetry_data:
            collected_at = telemetry_data["collected_at"]
            if isinstance(collected_at, str):
                try:
                    telemetry_data["collected_at"] = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
                except ValueError:
                    raise BadRequestException("Invalid collected_at timestamp format")

        # Validate numeric ranges
        if "cpu_usage_percent" in telemetry_data:
            cpu = telemetry_data["cpu_usage_percent"]
            if cpu is not None and (cpu < 0 or cpu > 100):
                raise BadRequestException("cpu_usage_percent must be between 0 and 100")

        if "memory_usage_percent" in telemetry_data:
            mem = telemetry_data["memory_usage_percent"]
            if mem is not None and (mem < 0 or mem > 100):
                raise BadRequestException("memory_usage_percent must be between 0 and 100")

        if "disk_usage_percent" in telemetry_data:
            disk = telemetry_data["disk_usage_percent"]
            if disk is not None and (disk < 0 or disk > 100):
                raise BadRequestException("disk_usage_percent must be between 0 and 100")

        # Validate network_interfaces is a list if present
        if "network_interfaces" in telemetry_data:
            ifaces = telemetry_data["network_interfaces"]
            if ifaces is not None and not isinstance(ifaces, list):
                raise BadRequestException("network_interfaces must be an array")

    async def query_telemetry(
        self,
        device_id: UUID,
        owner_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DeviceTelemetry]:
        """Query telemetry for a device (with ownership verification)."""
        # Verify device ownership
        device = await self._device_repository.get_by_id(device_id)
        if device is None:
            raise DeviceNotFoundException()

        if device.owner_id != owner_id:
            raise DeviceNotFoundException()

        return await self._telemetry_repository.get_by_device(device_id, limit, offset)

    async def get_latest_telemetry(
        self,
        device_id: UUID,
        owner_id: UUID,
    ) -> DeviceTelemetry | None:
        """Get the most recent telemetry for a device."""
        telemetry_list = await self.query_telemetry(device_id, owner_id, limit=1)
        return telemetry_list[0] if telemetry_list else None
