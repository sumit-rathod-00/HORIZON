from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset


class AssetRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, asset: Asset) -> Asset:
        self._session.add(asset)
        await self._session.flush()
        await self._session.refresh(asset)
        return asset

    async def get_by_id(self, asset_id: UUID) -> Asset | None:
        stmt = select(Asset).where(Asset.id == asset_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID):
        stmt = select(Asset).where(Asset.project_id == project_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()