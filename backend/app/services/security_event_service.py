"""Security event service for managing security events."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DeviceNotFoundException
from app.models.security_event import SecurityEvent
from app.repositories.device_repository import DeviceRepository
from app.repositories.security_event_repository import SecurityEventRepository


class SecurityEventService:
    """Service for creating and managing security events."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._event_repository = SecurityEventRepository(session)
        self._device_repository = DeviceRepository(session)

    async def create_event(
        self,
        device_id: UUID,
        event_type: str,
        severity: str,
        title: str,
        description: str | None = None,
        evidence: dict | None = None,
        detection_source: str = "detection_engine",
    ) -> SecurityEvent:
        """Create a new security event."""
        # Verify device exists
        device = await self._device_repository.get_by_id(device_id)
        if device is None:
            raise DeviceNotFoundException()

        event = SecurityEvent(
            device_id=device_id,
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            evidence=evidence or {},
            detection_source=detection_source,
            status="open",
            detected_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        created = await self._event_repository.create(event)
        await self._session.commit()

        return created

    async def get_device_events(
        self,
        device_id: UUID,
        owner_id: UUID,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[SecurityEvent]:
        """Get security events for a device (with ownership verification)."""
        # Verify device ownership
        device = await self._device_repository.get_by_id(device_id)
        if device is None:
            raise DeviceNotFoundException()

        if device.owner_id != owner_id:
            raise DeviceNotFoundException()

        return await self._event_repository.get_by_device(
            device_id=device_id,
            limit=limit,
            offset=offset,
            status=status,
            severity=severity,
        )

    async def update_event_status(
        self,
        event_id: UUID,
        owner_id: UUID,
        new_status: str,
    ) -> SecurityEvent:
        """Update event status (with ownership verification)."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise DeviceNotFoundException()

        # Verify device ownership
        device = await self._device_repository.get_by_id(event.device_id)
        if device is None or device.owner_id != owner_id:
            raise DeviceNotFoundException()

        # Update status and timestamps
        event.status = new_status
        event.updated_at = datetime.now(timezone.utc)

        if new_status == "acknowledged" and event.acknowledged_at is None:
            event.acknowledged_at = datetime.now(timezone.utc)
        elif new_status == "resolved" and event.resolved_at is None:
            event.resolved_at = datetime.now(timezone.utc)

        updated = await self._event_repository.update(event)
        return updated
