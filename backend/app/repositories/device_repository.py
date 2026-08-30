"""Device repository for database operations."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device


class DeviceRepository:
    """Repository for device database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, device: Device) -> Device:
        """Create a new device."""
        self._session.add(device)
        await self._session.flush()
        await self._session.refresh(device)
        return device

    async def get_by_id(self, device_id: UUID) -> Device | None:
        """Get device by ID."""
        stmt = select(Device).where(Device.id == device_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> list[Device]:
        """Get all devices owned by a user."""
        stmt = (
            select(Device)
            .where(Device.owner_id == owner_id)
            .order_by(Device.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, device: Device) -> Device:
        """Update device information."""
        await self._session.commit()
        await self._session.refresh(device)
        return device

    async def delete(self, device: Device) -> None:
        """Delete a device."""
        await self._session.delete(device)
        await self._session.commit()
