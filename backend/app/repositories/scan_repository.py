from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan


class ScanRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, scan: Scan) -> Scan:
        self._session.add(scan)

        await self._session.commit()
        await self._session.refresh(scan)

        return scan

    async def get_by_asset(self, asset_id: UUID) -> list[Scan]:
        stmt = select(Scan).where(Scan.asset_id == asset_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, scan_id: UUID) -> Scan | None:
        stmt = select(Scan).where(Scan.id == scan_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        scan: Scan,
        status: str,
    ) -> Scan:
        scan.status = status

        await self._session.commit()
        await self._session.refresh(scan)

        return scan

    async def delete(
        self,
        scan: Scan,
    ) -> None:
        await self._session.delete(scan)
        await self._session.commit()