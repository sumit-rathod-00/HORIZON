"""Security correlation engine for connecting devices, assets, vulnerabilities, telemetry, and events."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.device import Device
from app.models.device_telemetry import DeviceTelemetry
from app.models.security_event import SecurityEvent
from app.models.vulnerability import Vulnerability

logger = logging.getLogger(__name__)


@dataclass
class SecurityCorrelation:
    """Correlated security data for a single entity."""

    device_id: UUID | None
    device_name: str | None
    device_status: str | None
    asset_id: UUID | None
    asset_ip: str | None
    asset_hostname: str | None
    vulnerability_count: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    open_events: int
    critical_events: int
    last_telemetry: datetime | None
    firewall_enabled: bool | None
    antivirus_enabled: bool | None
    risk_score: float


@dataclass
class RiskSummary:
    """Risk summary across all assets and devices."""

    total_devices: int
    total_assets: int
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    total_events: int
    critical_events: int
    active_devices: int
    unhealthy_devices: int
    average_risk_score: float
    highest_risk_device: str | None
    highest_risk_score: float


class SecurityCorrelationService:
    """
    Service for correlating security data across devices, assets, vulnerabilities,
    telemetry, and security events.

    This service provides a unified view of security state by connecting:
    - Device health and status
    - Asset vulnerabilities
    - Security events
    - Telemetry data
    - Risk scores
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_device_correlation(self, device_id: UUID, user_id: UUID) -> SecurityCorrelation | None:
        """
        Get correlated security data for a specific device.

        Combines:
        - Device status and health
        - Associated asset vulnerabilities
        - Recent security events
        - Latest telemetry
        - Calculated risk score
        """
        # Get device
        device_stmt = select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id,
        )
        device_result = await self._session.execute(device_stmt)
        device = device_result.scalar_one_or_none()

        if not device:
            return None

        # Get associated asset
        asset_stmt = select(Asset).where(
            Asset.device_id == device_id,
            Asset.user_id == user_id,
        )
        asset_result = await self._session.execute(asset_stmt)
        asset = asset_result.scalar_one_or_none()

        # Get vulnerability counts
        vuln_counts = {"total": 0, "critical": 0, "high": 0}
        if asset:
            vuln_stmt = (
                select(
                    func.count(Vulnerability.id).label("total"),
                    func.count(Vulnerability.id)
                    .filter(Vulnerability.severity == "Critical")
                    .label("critical"),
                    func.count(Vulnerability.id)
                    .filter(Vulnerability.severity == "High")
                    .label("high"),
                )
                .where(
                    Vulnerability.asset_id == asset.id,
                    Vulnerability.status == "Open",
                )
            )
            vuln_result = await self._session.execute(vuln_stmt)
            vuln_row = vuln_result.one()
            vuln_counts = {
                "total": vuln_row.total or 0,
                "critical": vuln_row.critical or 0,
                "high": vuln_row.high or 0,
            }

        # Get security event counts
        event_stmt = (
            select(
                func.count(SecurityEvent.id).label("total"),
                func.count(SecurityEvent.id)
                .filter(SecurityEvent.severity.in_(["critical", "high"]))
                .label("critical"),
            )
            .where(
                SecurityEvent.device_id == device_id,
                SecurityEvent.status == "open",
            )
        )
        event_result = await self._session.execute(event_stmt)
        event_row = event_result.one()
        event_counts = {
            "total": event_row.total or 0,
            "critical": event_row.critical or 0,
        }

        # Get latest telemetry
        telemetry_stmt = (
            select(DeviceTelemetry)
            .where(DeviceTelemetry.device_id == device_id)
            .order_by(DeviceTelemetry.collected_at.desc())
            .limit(1)
        )
        telemetry_result = await self._session.execute(telemetry_stmt)
        telemetry = telemetry_result.scalar_one_or_none()

        # Calculate composite risk score
        risk_score = self._calculate_risk_score(
            vulnerability_count=vuln_counts["total"],
            critical_vulnerabilities=vuln_counts["critical"],
            high_vulnerabilities=vuln_counts["high"],
            critical_events=event_counts["critical"],
            device_status=device.status,
            firewall_enabled=telemetry.firewall_enabled if telemetry else None,
            antivirus_enabled=telemetry.antivirus_enabled if telemetry else None,
        )

        return SecurityCorrelation(
            device_id=device.id,
            device_name=device.name,
            device_status=device.status,
            asset_id=asset.id if asset else None,
            asset_ip=asset.ip_address if asset else None,
            asset_hostname=asset.hostname if asset else None,
            vulnerability_count=vuln_counts["total"],
            critical_vulnerabilities=vuln_counts["critical"],
            high_vulnerabilities=vuln_counts["high"],
            open_events=event_counts["total"],
            critical_events=event_counts["critical"],
            last_telemetry=telemetry.collected_at if telemetry else None,
            firewall_enabled=telemetry.firewall_enabled if telemetry else None,
            antivirus_enabled=telemetry.antivirus_enabled if telemetry else None,
            risk_score=risk_score,
        )

    async def get_risk_summary(self, user_id: UUID) -> RiskSummary:
        """
        Get organization-wide risk summary.

        Aggregates:
        - Total devices, assets, vulnerabilities
        - Critical/high severity counts
        - Device health statistics
        - Average risk score
        - Highest risk device
        """
        # Get device counts
        device_stmt = (
            select(
                func.count(Device.id).label("total"),
                func.count(Device.id)
                .filter(Device.status == "active")
                .label("active"),
            )
            .where(Device.user_id == user_id)
        )
        device_result = await self._session.execute(device_stmt)
        device_row = device_result.one()
        device_counts = {
            "total": device_row.total or 0,
            "active": device_row.active or 0,
        }

        # Get asset count
        asset_stmt = select(func.count(Asset.id)).where(Asset.user_id == user_id)
        asset_result = await self._session.execute(asset_stmt)
        asset_count = asset_result.scalar() or 0

        # Get vulnerability counts
        vuln_stmt = (
            select(
                func.count(Vulnerability.id).label("total"),
                func.count(Vulnerability.id)
                .filter(Vulnerability.severity == "Critical")
                .label("critical"),
                func.count(Vulnerability.id)
                .filter(Vulnerability.severity == "High")
                .label("high"),
            )
            .join(Asset, Vulnerability.asset_id == Asset.id)
            .where(
                Asset.user_id == user_id,
                Vulnerability.status == "Open",
            )
        )
        vuln_result = await self._session.execute(vuln_stmt)
        vuln_row = vuln_result.one()
        vuln_counts = {
            "total": vuln_row.total or 0,
            "critical": vuln_row.critical or 0,
            "high": vuln_row.high or 0,
        }

        # Get event counts
        event_stmt = (
            select(
                func.count(SecurityEvent.id).label("total"),
                func.count(SecurityEvent.id)
                .filter(SecurityEvent.severity.in_(["critical", "high"]))
                .label("critical"),
            )
            .join(Device, SecurityEvent.device_id == Device.id)
            .where(
                Device.user_id == user_id,
                SecurityEvent.status == "open",
            )
        )
        event_result = await self._session.execute(event_stmt)
        event_row = event_result.one()
        event_counts = {
            "total": event_row.total or 0,
            "critical": event_row.critical or 0,
        }

        # Calculate unhealthy devices (firewall/AV disabled, stale telemetry)
        unhealthy_count = await self._count_unhealthy_devices(user_id)

        # Calculate average risk and find highest risk device
        devices = await self._get_all_devices(user_id)
        risk_scores = []
        highest_risk_device = None
        highest_risk_score = 0.0

        for device in devices:
            correlation = await self.get_device_correlation(device.id, user_id)
            if correlation:
                risk_scores.append(correlation.risk_score)
                if correlation.risk_score > highest_risk_score:
                    highest_risk_score = correlation.risk_score
                    highest_risk_device = correlation.device_name

        average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

        return RiskSummary(
            total_devices=device_counts["total"],
            total_assets=asset_count,
            total_vulnerabilities=vuln_counts["total"],
            critical_vulnerabilities=vuln_counts["critical"],
            high_vulnerabilities=vuln_counts["high"],
            total_events=event_counts["total"],
            critical_events=event_counts["critical"],
            active_devices=device_counts["active"],
            unhealthy_devices=unhealthy_count,
            average_risk_score=round(average_risk, 1),
            highest_risk_device=highest_risk_device,
            highest_risk_score=round(highest_risk_score, 1),
        )

    async def _count_unhealthy_devices(self, user_id: UUID) -> int:
        """Count devices with health issues."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)

        # Devices with disabled security or stale telemetry
        stmt = (
            select(func.count(func.distinct(Device.id)))
            .select_from(Device)
            .outerjoin(
                DeviceTelemetry,
                (DeviceTelemetry.device_id == Device.id)
                & (DeviceTelemetry.collected_at > cutoff),
            )
            .where(
                Device.user_id == user_id,
                Device.status != "revoked",
            )
            .where(
                (DeviceTelemetry.firewall_enabled == False)  # noqa: E712
                | (DeviceTelemetry.antivirus_enabled == False)  # noqa: E712
                | (DeviceTelemetry.id == None)  # noqa: E711
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def _get_all_devices(self, user_id: UUID) -> list[Device]:
        """Get all devices for a user."""
        stmt = select(Device).where(Device.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    def _calculate_risk_score(
        self,
        vulnerability_count: int,
        critical_vulnerabilities: int,
        high_vulnerabilities: int,
        critical_events: int,
        device_status: str,
        firewall_enabled: bool | None,
        antivirus_enabled: bool | None,
    ) -> float:
        """
        Calculate composite risk score (0-10).

        Factors:
        - Vulnerability count and severity
        - Critical security events
        - Device health (firewall, antivirus)
        - Device status (active/inactive)
        """
        score = 0.0

        # Vulnerabilities (max 5 points)
        score += min(vulnerability_count * 0.5, 3.0)
        score += critical_vulnerabilities * 1.0
        score += high_vulnerabilities * 0.5

        # Security events (max 3 points)
        score += min(critical_events * 1.5, 3.0)

        # Device health (max 2 points)
        if firewall_enabled is False:
            score += 1.0
        if antivirus_enabled is False:
            score += 1.0

        # Device status penalty
        if device_status in ["inactive", "stale"]:
            score += 0.5

        return min(round(score, 1), 10.0)
