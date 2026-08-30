"""Device service for device management and authorization."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, DeviceNotFoundException
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.services.audit_log_service import AuditLogService


class DeviceService:
    """Service for device enrollment, management, and authorization."""

    VALID_STATUSES = {"pending", "active", "inactive", "revoked"}

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = DeviceRepository(session)
        self._audit_service = AuditLogService(session)

    async def enroll_device(
        self,
        owner_id: UUID,
        name: str,
        platform: str | None = None,
        operating_system: str | None = None,
        device_type: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[Device, str]:
        """
        Enroll a new device for a user.

        Returns:
            Tuple of (device, enrollment_token)
        """
        normalized_name = name.strip()
        if not normalized_name:
            raise BadRequestException("Device name must not be empty")

        # Generate secure enrollment token
        enrollment_token = secrets.token_urlsafe(32)
        enrollment_token_hash = bcrypt.hash(enrollment_token)

        device = Device(
            owner_id=owner_id,
            name=normalized_name,
            platform=platform.strip() if platform else None,
            operating_system=operating_system.strip() if operating_system else None,
            device_type=device_type.strip() if device_type else None,
            enrollment_token_hash=enrollment_token_hash,
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        created_device = await self._repository.create(device)
        await self._session.commit()

        await self._audit_service.log_event(
            action="device.enroll",
            actor_id=owner_id,
            target_type="device",
            target_id=str(created_device.id),
            result="success",
            details=f"Device enrolled: {normalized_name}",
            ip_address=ip_address,
        )

        return created_device, enrollment_token

    async def get_device(self, device_id: UUID, owner_id: UUID) -> Device:
        """Get a device, verifying ownership."""
        device = await self._repository.get_by_id(device_id)
        if device is None:
            raise DeviceNotFoundException()

        if device.owner_id != owner_id:
            raise DeviceNotFoundException()

        return device

    async def list_user_devices(self, owner_id: UUID) -> list[Device]:
        """List all devices owned by a user."""
        return await self._repository.get_by_owner(owner_id)

    async def update_device(
        self,
        device_id: UUID,
        owner_id: UUID,
        name: str | None = None,
        platform: str | None = None,
        operating_system: str | None = None,
        device_type: str | None = None,
        status: str | None = None,
    ) -> Device:
        """Update device information, verifying ownership."""
        device = await self.get_device(device_id, owner_id)

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise BadRequestException("Device name must not be empty")
            device.name = normalized_name

        if platform is not None:
            device.platform = platform.strip() if platform else None

        if operating_system is not None:
            device.operating_system = operating_system.strip() if operating_system else None

        if device_type is not None:
            device.device_type = device_type.strip() if device_type else None

        if status is not None:
            normalized_status = status.strip().lower()
            if normalized_status not in self.VALID_STATUSES:
                raise BadRequestException(f"Invalid device status: {status}")
            device.status = normalized_status

        device.updated_at = datetime.now(timezone.utc)

        updated = await self._repository.update(device)

        await self._audit_service.log_event(
            action="device.update",
            actor_id=owner_id,
            target_type="device",
            target_id=str(device_id),
            result="success",
            details=f"Device updated: {device.name}",
        )

        return updated

    async def revoke_device(
        self,
        device_id: UUID,
        owner_id: UUID,
        ip_address: str | None = None,
    ) -> Device:
        """Revoke a device, preventing further operations."""
        device = await self.get_device(device_id, owner_id)

        if device.status == "revoked":
            return device

        device.status = "revoked"
        device.updated_at = datetime.now(timezone.utc)

        updated = await self._repository.update(device)

        await self._audit_service.log_event(
            action="device.revoke",
            actor_id=owner_id,
            target_type="device",
            target_id=str(device_id),
            result="success",
            details=f"Device revoked: {device.name}",
            ip_address=ip_address,
        )

        return updated

    async def activate_device(
        self,
        device_id: UUID,
        owner_id: UUID,
    ) -> Device:
        """Activate a device."""
        device = await self.get_device(device_id, owner_id)

        device.status = "active"
        device.last_seen = datetime.now(timezone.utc)
        device.updated_at = datetime.now(timezone.utc)

        updated = await self._repository.update(device)

        await self._audit_service.log_event(
            action="device.activate",
            actor_id=owner_id,
            target_type="device",
            target_id=str(device_id),
            result="success",
            details=f"Device activated: {device.name}",
        )

        return updated

    async def update_last_seen(self, device_id: UUID) -> None:
        """Update device last_seen timestamp (for heartbeat)."""
        device = await self._repository.get_by_id(device_id)
        if device and device.status == "active":
            device.last_seen = datetime.now(timezone.utc)
            device.updated_at = datetime.now(timezone.utc)
            await self._repository.update(device)
