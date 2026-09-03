"""Test heartbeat service functionality."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.heartbeat_service import HeartbeatService
from app.models.device import Device
from app.core.exceptions import UnauthorizedException, BadRequestException, DeviceNotFoundException


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_device():
    device = Device(
        id=uuid4(),
        owner_id=uuid4(),
        name="Test Device",
        platform="Windows",
        operating_system="Windows 11",
        device_type="Laptop",
        enrollment_token_hash="$2b$12$test_hash",
        status="pending",
        last_seen=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return device


@pytest.mark.asyncio
async def test_heartbeat_accepts_valid_device(mock_session, mock_device):
    """Test that valid heartbeat is accepted."""
    service = HeartbeatService(mock_session)
    service._repository = AsyncMock()
    service._audit_service = AsyncMock()

    # Mock device lookup
    service._repository.get_by_id = AsyncMock(return_value=mock_device)
    service._repository.update = AsyncMock(return_value=mock_device)

    # Mock bcrypt verification
    import passlib.hash
    original_verify = passlib.hash.bcrypt.verify
    passlib.hash.bcrypt.verify = lambda token, hash: True

    try:
        device, message = await service.process_heartbeat(
            device_id=mock_device.id,
            enrollment_token="valid_token",
            agent_version="1.0.0",
            timestamp=datetime.now(timezone.utc),
            status="healthy",
        )

        assert device.status == "active"
        assert device.last_seen is not None
        assert "activated" in message.lower() or "accepted" in message.lower()
    finally:
        passlib.hash.bcrypt.verify = original_verify


@pytest.mark.asyncio
async def test_heartbeat_rejects_revoked_device(mock_session, mock_device):
    """Test that revoked device cannot send heartbeat."""
    service = HeartbeatService(mock_session)
    service._repository = AsyncMock()

    mock_device.status = "revoked"
    service._repository.get_by_id = AsyncMock(return_value=mock_device)

    # Mock bcrypt verification
    import passlib.hash
    passlib.hash.bcrypt.verify = lambda token, hash: True

    with pytest.raises(UnauthorizedException, match="revoked"):
        await service.process_heartbeat(
            device_id=mock_device.id,
            enrollment_token="valid_token",
            agent_version="1.0.0",
            timestamp=datetime.now(timezone.utc),
            status="healthy",
        )


@pytest.mark.asyncio
async def test_heartbeat_rejects_invalid_token(mock_session, mock_device):
    """Test that invalid enrollment token is rejected."""
    service = HeartbeatService(mock_session)
    service._repository = AsyncMock()

    service._repository.get_by_id = AsyncMock(return_value=mock_device)

    # Mock bcrypt verification to fail
    import passlib.hash
    passlib.hash.bcrypt.verify = lambda token, hash: False

    with pytest.raises(UnauthorizedException, match="Invalid"):
        await service.process_heartbeat(
            device_id=mock_device.id,
            enrollment_token="wrong_token",
            agent_version="1.0.0",
            timestamp=datetime.now(timezone.utc),
            status="healthy",
        )


@pytest.mark.asyncio
async def test_heartbeat_rejects_stale_timestamp(mock_session, mock_device):
    """Test that heartbeat with stale timestamp is rejected."""
    service = HeartbeatService(mock_session)
    service._repository = AsyncMock()
    service._repository.get_by_id = AsyncMock(return_value=mock_device)

    # Timestamp from 10 minutes ago
    old_timestamp = datetime.now(timezone.utc) - timedelta(minutes=10)

    with pytest.raises(BadRequestException, match="timestamp"):
        await service.process_heartbeat(
            device_id=mock_device.id,
            enrollment_token="valid_token",
            agent_version="1.0.0",
            timestamp=old_timestamp,
            status="healthy",
        )


@pytest.mark.asyncio
async def test_calculate_device_state_active(mock_device):
    """Test state calculation for active device."""
    service = HeartbeatService(AsyncMock())

    mock_device.last_seen = datetime.now(timezone.utc) - timedelta(seconds=60)
    mock_device.status = "active"

    state = await service.calculate_device_state(mock_device)
    assert state == "active"


@pytest.mark.asyncio
async def test_calculate_device_state_stale(mock_device):
    """Test state calculation for stale device."""
    service = HeartbeatService(AsyncMock())

    # Last seen 10 minutes ago (within timeout but past interval)
    mock_device.last_seen = datetime.now(timezone.utc) - timedelta(minutes=10)
    mock_device.status = "active"

    state = await service.calculate_device_state(mock_device)
    assert state == "stale"


@pytest.mark.asyncio
async def test_calculate_device_state_inactive(mock_device):
    """Test state calculation for inactive device."""
    service = HeartbeatService(AsyncMock())

    # Last seen 20 minutes ago (beyond timeout)
    mock_device.last_seen = datetime.now(timezone.utc) - timedelta(minutes=20)
    mock_device.status = "active"

    state = await service.calculate_device_state(mock_device)
    assert state == "inactive"


@pytest.mark.asyncio
async def test_calculate_device_state_revoked(mock_device):
    """Test state calculation for revoked device."""
    service = HeartbeatService(AsyncMock())

    mock_device.status = "revoked"
    mock_device.last_seen = datetime.now(timezone.utc)

    state = await service.calculate_device_state(mock_device)
    assert state == "revoked"
