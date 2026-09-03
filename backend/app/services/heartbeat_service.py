"""Heartbeat service for device health monitoring."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, DeviceNotFoundException, BadRequestException
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.services.audit_log_service import AuditLogService


class HeartbeatService:
    """Service for processing device heartbeat and maintaining device health state."""

    HEARTBEAT_INTERVAL_SECONDS = 300  # 5 minutes
    HEARTBEAT_TIMEOUT_SECONDS = 900   # 15 minutes (3x interval)

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = DeviceRepository(session)
        self._audit_service = AuditLogService(session)

    async def process_heartbeat(
        self,
        device_id: UUID | None,
        enrollment_token: str,
        agent_version: str,
        timestamp: datetime,
        status: str,
        ip_address: str | None = None,
    ) -> tuple[Device, str]:
        """
        Process device heartbeat and update device state.

        Returns:
            Tuple of (device, message)
        """
        # Validate timestamp (reject if too far in future or too old)
        now = datetime.now(timezone.utc)
        time_diff = abs((timestamp - now).total_seconds())

        if time_diff > 300:  # 5 minutes tolerance
            raise BadRequestException("Heartbeat timestamp is invalid (too far from server time)")

        # Find device by enrollment token
        device = await self._authenticate_device(device_id, enrollment_token)

        # Check if device is revoked
        if device.status == "revoked":
            raise UnauthorizedException("Device has been revoked")

        # Update device state
        old_status = device.status
        device.last_seen = now
        device.status = "active"
        device.updated_at = now

        await self._repository.update(device)
        await self._session.commit()

        # Audit log heartbeat (minimal logging to avoid excessive entries)
        if old_status != "active":
            await self._audit_service.log_event(
                action="device.heartbeat",
                actor_id=device.owner_id,
                target_type="device",
                target_id=str(device.id),
                result="success",
                details=f"Device {device.name} became active (agent {agent_version})",
                ip_address=ip_address,
            )

        message = "Heartbeat accepted"
        if old_status == "pending":
            message = "Device activated"

        return device, message

    async def _authenticate_device(
        self,
        device_id: UUID | None,
        enrollment_token: str,
    ) -> Device:
        """
        Authenticate device using enrollment token.

        Returns the authenticated device or raises UnauthorizedException.
        """
        if not enrollment_token:
            raise UnauthorizedException("Enrollment token required")

        # If device_id provided, verify it matches the token
        if device_id:
            device = await self._repository.get_by_id(device_id)
            if device is None:
                raise DeviceNotFoundException()
        else:
            # First heartbeat - find device by token hash
            # For efficiency, we'd need to query by token hash
            # For now, we'll validate that device_id is provided after first activation
            raise BadRequestException("Device ID required (use enrollment token on first heartbeat)")

        # Verify enrollment token hash
        if not device.enrollment_token_hash:
            raise UnauthorizedException("Device enrollment token not configured")

        if not bcrypt.verify(enrollment_token, device.enrollment_token_hash):
            raise UnauthorizedException("Invalid enrollment token")

        return device

    async def calculate_device_state(self, device: Device) -> str:
        """
        Calculate device state based on last_seen timestamp.

        Returns: 'active', 'stale', 'inactive', or 'revoked'
        """
        if device.status == "revoked":
            return "revoked"

        if device.last_seen is None:
            return "inactive"

        now = datetime.now(timezone.utc)
        seconds_since_seen = (now - device.last_seen).total_seconds()

        if seconds_since_seen <= self.HEARTBEAT_INTERVAL_SECONDS:
            return "active"
        elif seconds_since_seen <= self.HEARTBEAT_TIMEOUT_SECONDS:
            return "stale"
        else:
            return "inactive"

    async def update_stale_devices(self) -> int:
        """
        Background job to update device states based on heartbeat timeout.

        Returns count of devices updated.
        """
        # This would be called periodically by a background worker
        # For Layer 2, we'll keep it simple and calculate state on-demand
        # Future enhancement: background job updates inactive devices
        return 0
