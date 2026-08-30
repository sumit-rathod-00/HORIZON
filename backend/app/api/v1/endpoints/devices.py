"""Device management API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceEnrollResponse, DeviceRead, DeviceUpdate
from app.security.dependencies import get_current_user
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "/enroll",
    response_model=DeviceEnrollResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_device(
    device_in: DeviceCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll a new device for the authenticated user.

    Returns the device information and an enrollment token that should be
    securely stored by the device for authentication.
    """
    service = DeviceService(db)

    # Get client IP for audit logging
    ip_address = request.client.host if request.client else None

    device, enrollment_token = await service.enroll_device(
        owner_id=current_user.id,
        name=device_in.name,
        platform=device_in.platform,
        operating_system=device_in.operating_system,
        device_type=device_in.device_type,
        ip_address=ip_address,
    )

    return DeviceEnrollResponse(
        device=device,
        enrollment_token=enrollment_token,
        message="Device enrolled successfully. Store the enrollment token securely.",
    )


@router.get("", response_model=list[DeviceRead])
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all devices owned by the authenticated user."""
    service = DeviceService(db)
    return await service.list_user_devices(current_user.id)


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific device (ownership verified)."""
    service = DeviceService(db)
    return await service.get_device(device_id, current_user.id)


@router.patch("/{device_id}", response_model=DeviceRead)
async def update_device(
    device_id: UUID,
    device_update: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update device information (ownership verified)."""
    service = DeviceService(db)
    return await service.update_device(
        device_id=device_id,
        owner_id=current_user.id,
        name=device_update.name,
        platform=device_update.platform,
        operating_system=device_update.operating_system,
        device_type=device_update.device_type,
        status=device_update.status,
    )


@router.post("/{device_id}/revoke", response_model=DeviceRead)
async def revoke_device(
    device_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a device, preventing further operations.

    This action is audited for security purposes.
    """
    service = DeviceService(db)

    # Get client IP for audit logging
    ip_address = request.client.host if request.client else None

    return await service.revoke_device(
        device_id=device_id,
        owner_id=current_user.id,
        ip_address=ip_address,
    )


@router.post("/{device_id}/activate", response_model=DeviceRead)
async def activate_device(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a device (set status to active)."""
    service = DeviceService(db)
    return await service.activate_device(
        device_id=device_id,
        owner_id=current_user.id,
    )
