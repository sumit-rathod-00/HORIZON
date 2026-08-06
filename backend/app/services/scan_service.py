from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan
from app.repositories.scan_repository import ScanRepository
from app.core.exceptions import ScanNotFoundException


class ScanService:
    def __init__(self, session: AsyncSession):
        self._repository = ScanRepository(session)

    async def create_scan(
        self,
        asset_id: UUID,
        scanner: str,
    ) -> Scan:

        scan = Scan(
            asset_id=asset_id,
            scanner=scanner,
            status="Pending",
            started_at=datetime.utcnow(),
        )

        return await self._repository.create(scan)

    async def list_scans(
        self,
        asset_id: UUID,
    ) -> list[Scan]:

        return await self._repository.get_by_asset(asset_id)

    async def update_scan_status(
        self,
        scan_id: UUID,
        status: str,
    ) -> Scan:

        scan = await self._repository.get_by_id(scan_id)

        if scan is None:
            raise ScanNotFoundException()

        scan.status = status

        if status == "Completed":
            scan.completed_at = datetime.utcnow()

        return await self._repository.update_status(
            scan,
            status,
        )

    async def delete_scan(
        self,
        scan_id: UUID,
    ) -> None:

        scan = await self._repository.get_by_id(scan_id)

        if scan is None:
            raise ScanNotFoundException()

        await self._repository.delete(scan)