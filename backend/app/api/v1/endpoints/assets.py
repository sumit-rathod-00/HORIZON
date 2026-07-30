from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.asset import AssetCreate, AssetRead
from app.services.asset_service import AssetService

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


@router.post(
    "/{project_id}",
    response_model=AssetRead,
)
async def create_asset(
    project_id: UUID,
    asset_in: AssetCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AssetService(db)

    return await service.create_asset(
        project_id=project_id,
        name=asset_in.name,
        asset_type=asset_in.asset_type,
        ip_address=asset_in.ip_address,
    )


@router.get(
    "/{project_id}",
    response_model=list[AssetRead],
)
async def list_assets(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = AssetService(db)

    return await service.list_assets(project_id)