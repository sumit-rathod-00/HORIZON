"""Security event repository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security_event import SecurityEvent


class SecurityEventRepository:
    """Repository for security event database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: SecurityEvent) -> SecurityEvent:
        """Create a new security event."""
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def get_by_id(self, event_id: UUID) -> SecurityEvent | None:
        """Get event by ID."""
        stmt = select(SecurityEvent).where(SecurityEvent.id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_device(
        self,
        device_id: UUID,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[SecurityEvent]:
        """Get events for a device with optional filters."""
        stmt = (
            select(SecurityEvent)
            .where(SecurityEvent.device_id == device_id)
        )

        if status:
            stmt = stmt.where(SecurityEvent.status == status)

        if severity:
            stmt = stmt.where(SecurityEvent.severity == severity)

        stmt = stmt.order_by(SecurityEvent.detected_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, event: SecurityEvent) -> SecurityEvent:
        """Update an event."""
        await self._session.commit()
        await self._session.refresh(event)
        return event
