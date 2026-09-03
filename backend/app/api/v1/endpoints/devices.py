"""Device management API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceEnrollResponse,
    DeviceRead,
    DeviceUpdate,
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
    TelemetryIngest,
    TelemetryResponse,
)
from app.security.dependencies import get_current_user
from app.services.device_service import DeviceService
from app.services.heartbeat_service import HeartbeatService
from app.services.telemetry_service import TelemetryService

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


@router.post("/heartbeat", response_model=DeviceHeartbeatResponse, status_code=status.HTTP_200_OK)
async def device_heartbeat(
    heartbeat: DeviceHeartbeatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Device agent heartbeat endpoint.

    Authenticates device using enrollment token and updates device state.
    """
    service = HeartbeatService(db)

    # Get client IP for audit logging
    ip_address = request.client.host if request.client else None

    device, message = await service.process_heartbeat(
        device_id=heartbeat.device_id,
        enrollment_token=heartbeat.enrollment_token,
        agent_version=heartbeat.agent_version,
        timestamp=heartbeat.timestamp,
        status=heartbeat.status,
        ip_address=ip_address,
    )

    return DeviceHeartbeatResponse(
        device_id=device.id,
        status=device.status,
        heartbeat_interval_seconds=HeartbeatService.HEARTBEAT_INTERVAL_SECONDS,
        telemetry_enabled=True,
        message=message,
    )


@router.post("/{device_id}/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    device_id: UUID,
    telemetry: TelemetryIngest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest telemetry from device agent.

    Requires device authentication via enrollment token in request body.
    """
    service = TelemetryService(db)

    # Get enrollment token from header or body
    enrollment_token = request.headers.get("X-Enrollment-Token", "")

    if not enrollment_token:
        raise UnauthorizedException("X-Enrollment-Token header required")

    telemetry_record = await service.ingest_telemetry(
        device_id=device_id,
        enrollment_token=enrollment_token,
        telemetry_data=telemetry.model_dump(),
    )

    return TelemetryResponse(
        telemetry_id=telemetry_record.id,
        status="accepted",
        received_at=telemetry_record.received_at,
    )


@router.get("/{device_id}/telemetry", response_model=list[dict])
async def get_device_telemetry(
    device_id: UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get telemetry history for a device (ownership verified)."""
    service = TelemetryService(db)

    telemetry_records = await service.query_telemetry(
        device_id=device_id,
        owner_id=current_user.id,
        limit=min(limit, 1000),
        offset=offset,
    )

    return [
        {
            "id": str(t.id),
            "collected_at": t.collected_at.isoformat(),
            "cpu_usage_percent": t.cpu_usage_percent,
            "memory_usage_percent": t.memory_usage_percent,
            "disk_usage_percent": t.disk_usage_percent,
            "firewall_enabled": t.firewall_enabled,
            "antivirus_enabled": t.antivirus_enabled,
            "os_updates_pending": t.os_updates_pending,
        }
        for t in telemetry_records
    ]


@router.get("/{device_id}/events", response_model=list[dict])
async def get_device_events(
    device_id: UUID,
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    severity: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get security events for a device (ownership verified)."""
    from app.services.security_event_service import SecurityEventService

    service = SecurityEventService(db)

    events = await service.get_device_events(
        device_id=device_id,
        owner_id=current_user.id,
        limit=min(limit, 1000),
        offset=offset,
        status=status,
        severity=severity,
    )

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "severity": e.severity,
            "title": e.title,
            "description": e.description,
            "status": e.status,
            "detected_at": e.detected_at.isoformat(),
            "evidence": e.evidence,
        }
        for e in events
    ]

