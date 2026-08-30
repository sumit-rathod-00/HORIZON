from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan_result import ScanResult


class ScanResultRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_many(self, results: list[ScanResult]) -> None:
        if results:
            self._session.add_all(results)
            await self._session.flush()

    async def get_by_scan(self, scan_id: UUID) -> list[ScanResult]:
        stmt = select(ScanResult).where(ScanResult.scan_id == scan_id).order_by(ScanResult.port)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
