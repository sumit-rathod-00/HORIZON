from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan
from app.models.asset import Asset
from app.repositories.scan_repository import ScanRepository
from app.services.nmap_scanner import NmapScanner
from app.services.scan_service import ScanService


class ScannerService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._scan_repository = ScanRepository(session)
        self._scan_service = ScanService(session)
        self._nmap = NmapScanner()

    async def run_scan(
        self,
        scan_id: UUID,
    ) -> None:
        scan = await self._scan_repository.get_by_id(scan_id)

        if scan is None:
            return

        asset = await self._session.get(
            Asset,
            scan.asset_id,
        )

        if asset is None or not asset.ip_address:
            await self._scan_service.update_scan_status(
                scan_id,
                "Failed",
            )
            return

        try:
            # Mark scan as running
            await self._scan_service.update_scan_status(
                scan_id,
                "Running",
            )

            # Execute Nmap against the asset IP
            result = await self._nmap.scan_host(
                asset.ip_address,
            )

            # Temporary: print the result so we can verify
            # Nmap is actually being executed.
            print("\n========== NMAP RESULT ==========")
            print(result)
            print("==================================\n")

            # For now we mark the scan completed.
            # Result parsing/storage comes in the next step.
            await self._scan_service.update_scan_status(
                scan_id,
                "Completed",
            )

        except Exception as exc:
            print(
                f"Nmap scan failed for scan {scan_id}: {exc}"
            )

            await self._scan_service.update_scan_status(
                scan_id,
                "Failed",
            )