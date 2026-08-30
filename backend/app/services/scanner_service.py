from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.asset import Asset
from app.repositories.scan_repository import ScanRepository
from app.services.nmap_scanner import NmapScanner
from app.services.scan_service import ScanService

logger = logging.getLogger(__name__)


class ScannerService:
    """Execute scans using a fresh database session owned by the background task."""

    def __init__(self):
        self._nmap = NmapScanner()

    async def run_scan(self, scan_id: UUID, owner_id: UUID) -> None:
        async with AsyncSessionLocal() as session:
            await self._run_scan(session, scan_id, owner_id)

    async def _run_scan(
        self,
        session: AsyncSession,
        scan_id: UUID,
        owner_id: UUID,
    ) -> None:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(session)

        scan = await scan_repository.get_by_id(scan_id)
        if scan is None:
            logger.warning("Scan %s no longer exists", scan_id)
            return

        try:
            asset = await session.get(Asset, scan.asset_id)
            if asset is None or not asset.ip_address:
                logger.warning("Scan %s has no valid asset target", scan_id)
                await scan_service.update_scan_status(
                    scan_id, "Failed", owner_id
                )
                return

            # Re-check ownership inside the background task. The asset may have
            # changed or been deleted after the HTTP request queued the task.
            await scan_service._verify_asset_owner(scan.asset_id, owner_id)

            await scan_service.update_scan_status(
                scan_id, "Running", owner_id
            )

            result = await self._nmap.scan_host(asset.ip_address)
            logger.info(
                "Nmap scan %s completed; output length=%d",
                scan_id,
                len(result),
            )

            await scan_service.update_scan_status(
                scan_id, "Completed", owner_id
            )
        except Exception:
            logger.exception("Nmap scan %s failed", scan_id)
            try:
                await scan_service.update_scan_status(
                    scan_id, "Failed", owner_id
                )
            except Exception:
                logger.exception(
                    "Unable to persist failed status for scan %s",
                    scan_id,
                )
