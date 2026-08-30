from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ProjectNotFoundException, ScanNotFoundException
from app.models.scan import Scan
from app.repositories.asset_repository import AssetRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.scan_repository import ScanRepository


class ScanService:
    def __init__(self, session: AsyncSession):
        self._repository = ScanRepository(session)
        self._asset_repository = AssetRepository(session)
        self._project_repository = ProjectRepository(session)

    async def _verify_asset_owner(self, asset_id: UUID, owner_id: UUID):
        asset = await self._asset_repository.get_by_id(asset_id)
        if asset is None:
            raise ProjectNotFoundException()

        project = await self._project_repository.get_by_id_and_owner(
            project_id=asset.project_id,
            owner_id=owner_id,
        )
        if project is None:
            raise ProjectNotFoundException()
        return asset

    async def _get_owned_scan(self, scan_id: UUID, owner_id: UUID) -> Scan:
        scan = await self._repository.get_by_id(scan_id)
        if scan is None:
            raise ScanNotFoundException()
        await self._verify_asset_owner(scan.asset_id, owner_id)
        return scan

    async def create_scan(
        self,
        asset_id: UUID,
        scanner: str,
        owner_id: UUID,
    ) -> Scan:
        await self._verify_asset_owner(asset_id, owner_id)

        normalized_scanner = scanner.strip()
        if not normalized_scanner:
            raise BadRequestException("Scanner must not be empty")

        scan = Scan(
            asset_id=asset_id,
            scanner=normalized_scanner,
            status="Pending",
            started_at=datetime.now(timezone.utc),
        )
        return await self._repository.create(scan)

    async def list_scans(
        self,
        asset_id: UUID,
        owner_id: UUID,
    ) -> list[Scan]:
        await self._verify_asset_owner(asset_id, owner_id)
        return await self._repository.get_by_asset(asset_id)

    async def update_scan_status(
        self,
        scan_id: UUID,
        status: str,
        owner_id: UUID,
    ) -> Scan:
        scan = await self._get_owned_scan(scan_id, owner_id)
        normalized_status = status.strip().lower()
        allowed_statuses = {
            "pending": "Pending",
            "running": "Running",
            "completed": "Completed",
            "failed": "Failed",
            "cancelled": "Cancelled",
        }

        if normalized_status not in allowed_statuses:
            raise BadRequestException(f"Invalid scan status: {status}")

        final_status = allowed_statuses[normalized_status]
        scan.status = final_status
        if final_status in {"Completed", "Failed", "Cancelled"}:
            scan.completed_at = datetime.now(timezone.utc)
        else:
            scan.completed_at = None

        return await self._repository.update_status(scan, final_status)

    async def delete_scan(
        self,
        scan_id: UUID,
        owner_id: UUID,
    ) -> None:
        scan = await self._get_owned_scan(scan_id, owner_id)
        await self._repository.delete(scan)
