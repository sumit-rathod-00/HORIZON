from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanRead, ScanStatusUpdate
from app.security.dependencies import get_current_user
from app.services.scan_service import ScanService
from app.services.scanner_service import ScannerService

router = APIRouter(
    prefix="/scans",
    tags=["Scans"],
)


@router.post(
    "/{asset_id}",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_scan(
    asset_id: UUID,
    scan: ScanCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    created_scan = await service.create_scan(
        asset_id=asset_id,
        scanner=scan.scanner,
        owner_id=current_user.id,
    )

    background_tasks.add_task(
        ScannerService().run_scan,
        created_scan.id,
        current_user.id,
    )

    return created_scan


@router.get(
    "/{asset_id}",
    response_model=list[ScanRead],
)
async def list_scans(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    return await service.list_scans(
        asset_id=asset_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{scan_id}",
    response_model=ScanRead,
)
async def update_scan(
    scan_id: UUID,
    scan_update: ScanStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    return await service.update_scan_status(
        scan_id=scan_id,
        status=scan_update.status,
        owner_id=current_user.id,
    )


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScanService(db)

    await service.delete_scan(
        scan_id=scan_id,
        owner_id=current_user.id,
    )

    return None
