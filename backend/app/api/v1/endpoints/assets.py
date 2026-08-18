from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProjectNotFoundException
from app.db.session import get_db
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetRead,
    AssetUpdate,
)
from app.security.dependencies import get_current_user
from app.services.asset_service import AssetService
from app.services.project_service import ProjectService

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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project_service = ProjectService(db)

    # Verify that the project belongs to the logged-in user
    await project_service.get_project(
        project_id=project_id,
        owner_id=current_user.id,
    )

    asset_service = AssetService(db)

    return await asset_service.create_asset(
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project_service = ProjectService(db)

    # Verify that the project belongs to the logged-in user
    await project_service.get_project(
        project_id=project_id,
        owner_id=current_user.id,
    )

    asset_service = AssetService(db)

    return await asset_service.list_assets(project_id)


@router.delete(
    "/{asset_id}",
    status_code=204,
)
async def delete_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset_service = AssetService(db)
    await asset_service.delete_asset(
        asset_id=asset_id,
        owner_id=current_user.id,
    )
    return None


@router.put(
    "/{asset_id}",
    response_model=AssetRead,
)
async def update_asset(
    asset_id: UUID,
    asset_in: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset_service = AssetService(db)
    return await asset_service.update_asset(
        asset_id=asset_id,
        owner_id=current_user.id,
        name=asset_in.name,
        asset_type=asset_in.asset_type,
        ip_address=asset_in.ip_address,
    )