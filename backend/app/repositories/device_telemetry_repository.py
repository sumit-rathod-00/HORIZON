"""Device telemetry repository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_telemetry import DeviceTelemetry


class DeviceTelemetryRepository:
    """Repository for device telemetry database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, telemetry: DeviceTelemetry) -> DeviceTelemetry:
        """Create a new telemetry record."""
        self._session.add(telemetry)
        await self._session.flush()
        await self._session.refresh(telemetry)
        return telemetry

    async def get_by_device(
        self,
        device_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DeviceTelemetry]:
        """Get telemetry records for a device, ordered by most recent first."""
        stmt = (
            select(DeviceTelemetry)
            .where(DeviceTelemetry.device_id == device_id)
            .order_by(DeviceTelemetry.collected_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest(self, device_id: UUID) -> DeviceTelemetry | None:
        """Get the most recent telemetry for a device."""
        stmt = (
            select(DeviceTelemetry)
            .where(DeviceTelemetry.device_id == device_id)
            .order_by(DeviceTelemetry.collected_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
