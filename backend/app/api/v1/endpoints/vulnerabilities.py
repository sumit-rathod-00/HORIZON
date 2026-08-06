from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.vulnerability import (
    VulnerabilityCreate,
    VulnerabilityRead,
    VulnerabilityUpdate,
)

from app.services.vulnerability_service import VulnerabilityService

router = APIRouter(
    prefix="/vulnerabilities",
    tags=["Vulnerabilities"],
)


@router.post(
    "/{asset_id}",
    response_model=VulnerabilityRead,
)
async def create_vulnerability(
    asset_id: UUID,
    vulnerability_in: VulnerabilityCreate,
    db: AsyncSession = Depends(get_db),
):
    service = VulnerabilityService(db)

    return await service.create_vulnerability(
        asset_id=asset_id,
        title=vulnerability_in.title,
        description=vulnerability_in.description,
        severity=vulnerability_in.severity,
        status=vulnerability_in.status,
    )


@router.get(
    "/{asset_id}",
    response_model=list[VulnerabilityRead],
)
async def list_vulnerabilities(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = VulnerabilityService(db)

    return await service.list_vulnerabilities(asset_id)

@router.patch(
    "/{vulnerability_id}",
    response_model=VulnerabilityRead,
)
async def update_vulnerability(
    vulnerability_id: UUID,
    vulnerability_in: VulnerabilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = VulnerabilityService(db)

    return await service.update_vulnerability(
        vulnerability_id,
        vulnerability_in.title,
        vulnerability_in.description,
        vulnerability_in.severity,
        vulnerability_in.status,
    )


@router.delete(
    "/{vulnerability_id}",
)
async def delete_vulnerability(
    vulnerability_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = VulnerabilityService(db)

    await service.delete_vulnerability(
        vulnerability_id
    )

    return {
        "message": "Vulnerability deleted successfully"
    }