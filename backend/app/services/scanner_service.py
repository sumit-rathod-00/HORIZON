from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.repositories.scan_repository import ScanRepository
from app.services.nmap_scanner import NmapScanner
from app.services.scan_service import ScanService

logger = logging.getLogger(__name__)


class ScannerService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._scan_repository = ScanRepository(session)
        self._scan_service = ScanService(session)
        self._nmap = NmapScanner()

    async def run_scan(self, scan_id: UUID) -> None:
        scan = await self._scan_repository.get_by_id(scan_id)
        if scan is None:
            logger.warning("Scan %s no longer exists", scan_id)
            return

        asset = await self._session.get(Asset, scan.asset_id)
        if asset is None or not asset.ip_address:
            logger.warning("Scan %s has no valid asset target", scan_id)
            await self._scan_service.update_scan_status(scan_id, "Failed")
            return

        try:
            await self._scan_service.update_scan_status(scan_id, "Running")
            result = await self._nmap.scan_host(asset.ip_address)
            logger.info("Nmap scan %s completed; output length=%d", scan_id, len(result))
            await self._scan_service.update_scan_status(scan_id, "Completed")
        except Exception:
            logger.exception("Nmap scan %s failed", scan_id)
            try:
                await self._scan_service.update_scan_status(scan_id, "Failed")
            except Exception:
                logger.exception("Unable to persist failed status for scan %s", scan_id)
