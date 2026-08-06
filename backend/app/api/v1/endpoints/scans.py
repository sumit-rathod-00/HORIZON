from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.scan import ScanCreate
from app.services.scan_service import ScanService

router = APIRouter(
    prefix="/scans",
    tags=["Scans"],
)


@router.post("/{asset_id}")
async def create_scan(
    asset_id: UUID,
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    return await service.create_scan(
        asset_id,
        scan.scanner,
    )


@router.get("/{asset_id}")
async def list_scans(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    return await service.list_scans(asset_id)


@router.patch("/{scan_id}")
async def update_scan(
    scan_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    return await service.update_scan_status(
        scan_id,
        status,
    )


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    await service.delete_scan(scan_id)

    return {
        "message": "Scan deleted successfully"
    }