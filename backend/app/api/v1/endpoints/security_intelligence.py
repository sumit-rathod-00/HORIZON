"""Security intelligence API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.security.dependencies import get_current_user
from app.models.device import Device
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.repositories.device_repository import DeviceRepository
from app.repositories.security_event_repository import SecurityEventRepository
from app.repositories.vulnerability_repository import VulnerabilityRepository
from app.schemas.security_intelligence import (
    CorrelationResponse,
    PrioritizedFindingResponse,
    RecommendationResponse,
    RiskSummaryResponse,
)
from app.services.security_correlation import SecurityCorrelationService
from app.services.security_prioritization import (
    PrioritizedFinding,
    SecurityPrioritizationService,
)
from app.services.security_recommendations import SecurityRecommendationService

router = APIRouter()


@router.get("/risk-summary", response_model=RiskSummaryResponse)
async def get_risk_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get organization-wide risk summary.

    Aggregates security metrics across all devices and assets.
    """
    correlation_service = SecurityCorrelationService(db)
    summary = await correlation_service.get_risk_summary(current_user.id)

    return RiskSummaryResponse(
        total_devices=summary.total_devices,
        total_assets=summary.total_assets,
        total_vulnerabilities=summary.total_vulnerabilities,
        critical_vulnerabilities=summary.critical_vulnerabilities,
        high_vulnerabilities=summary.high_vulnerabilities,
        total_events=summary.total_events,
        critical_events=summary.critical_events,
        active_devices=summary.active_devices,
        unhealthy_devices=summary.unhealthy_devices,
        average_risk_score=summary.average_risk_score,
        highest_risk_device=summary.highest_risk_device,
        highest_risk_score=summary.highest_risk_score,
    )


@router.get("/devices/{device_id}/correlation", response_model=CorrelationResponse)
async def get_device_correlation(
    device_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get correlated security data for a specific device.

    Includes device health, vulnerabilities, events, and risk score.
    """
    correlation_service = SecurityCorrelationService(db)
    correlation = await correlation_service.get_device_correlation(device_id, current_user.id)

    if not correlation:
        raise HTTPException(status_code=404, detail="Device not found")

    return CorrelationResponse(
        device_id=correlation.device_id,
        device_name=correlation.device_name,
        device_status=correlation.device_status,
        asset_id=correlation.asset_id,
        asset_ip=correlation.asset_ip,
        asset_hostname=correlation.asset_hostname,
        vulnerability_count=correlation.vulnerability_count,
        critical_vulnerabilities=correlation.critical_vulnerabilities,
        high_vulnerabilities=correlation.high_vulnerabilities,
        open_events=correlation.open_events,
        critical_events=correlation.critical_events,
        last_telemetry=correlation.last_telemetry,
        firewall_enabled=correlation.firewall_enabled,
        antivirus_enabled=correlation.antivirus_enabled,
        risk_score=correlation.risk_score,
    )


@router.get("/prioritized-findings", response_model=list[PrioritizedFindingResponse])
async def get_prioritized_findings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    min_priority: Annotated[float | None, Query(ge=0, le=100)] = None,
    severity: Annotated[list[str] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    Get prioritized security findings (vulnerabilities + events).

    Findings are ranked by priority score based on severity, risk, and context.
    """
    device_repo = DeviceRepository(db)
    vuln_repo = VulnerabilityRepository(db)
    event_repo = SecurityEventRepository(db)
    correlation_service = SecurityCorrelationService(db)

    # Get all devices for the user
    devices = await device_repo.get_by_user(current_user.id)

    # Collect prioritized findings
    findings: list[PrioritizedFinding] = []

    for device in devices:
        # Get device correlation for health context
        correlation = await correlation_service.get_device_correlation(device.id, current_user.id)
        if not correlation:
            continue

        device_unhealthy = (
            correlation.firewall_enabled is False or correlation.antivirus_enabled is False
        )

        # Get vulnerabilities for this device's asset
        if correlation.asset_id:
            vulnerabilities = await vuln_repo.get_by_asset(correlation.asset_id)
            for vuln in vulnerabilities:
                if vuln.status != "Open":
                    continue

                priority_score = SecurityPrioritizationService.calculate_priority_score(
                    severity=vuln.severity,
                    risk_score=vuln.risk_score,
                    cvss_score=vuln.cvss_score,
                    category=vuln.category,
                    detected_at=vuln.created_at,
                    device_unhealthy=device_unhealthy,
                )

                findings.append(
                    PrioritizedFinding(
                        id=vuln.id,
                        type="vulnerability",
                        title=vuln.title,
                        description=vuln.description or "",
                        severity=vuln.severity,
                        risk_score=vuln.risk_score or 0.0,
                        priority_score=priority_score,
                        device_id=device.id,
                        device_name=device.name,
                        asset_id=correlation.asset_id,
                        asset_ip=correlation.asset_ip,
                        detected_at=vuln.created_at,
                        cve_id=vuln.cve_id,
                        cwe_id=vuln.cwe_id,
                        cvss_score=vuln.cvss_score,
                        category=vuln.category,
                        evidence=vuln.evidence,
                        remediation=vuln.remediation,
                        status=vuln.status,
                    )
                )

        # Get security events for this device
        events = await event_repo.get_by_device(device.id, status="open", limit=100)
        for event in events:
            # Calculate risk score for events based on severity
            event_risk_score = {
                "critical": 10.0,
                "high": 7.5,
                "medium": 5.0,
                "low": 2.5,
                "info": 1.0,
            }.get(event.severity, 5.0)

            priority_score = SecurityPrioritizationService.calculate_priority_score(
                severity=event.severity,
                risk_score=event_risk_score,
                cvss_score=None,
                category="Security Event",
                detected_at=event.detected_at,
                device_unhealthy=device_unhealthy,
            )

            findings.append(
                PrioritizedFinding(
                    id=event.id,
                    type="event",
                    title=event.title,
                    description=event.description or "",
                    severity=event.severity,
                    risk_score=event_risk_score,
                    priority_score=priority_score,
                    device_id=device.id,
                    device_name=device.name,
                    asset_id=correlation.asset_id,
                    asset_ip=correlation.asset_ip,
                    detected_at=event.detected_at,
                    category="Security Event",
                    evidence=str(event.evidence) if event.evidence else None,
                    status=event.status,
                )
            )

    # Filter and sort findings
    filtered_findings = SecurityPrioritizationService.filter_by_priority(
        findings,
        min_priority=min_priority,
        severity_filter=severity,
        limit=limit,
    )

    # Convert to response model
    return [
        PrioritizedFindingResponse(
            id=f.id,
            type=f.type,
            title=f.title,
            description=f.description,
            severity=f.severity,
            risk_score=f.risk_score,
            priority_score=f.priority_score,
            device_id=f.device_id,
            device_name=f.device_name,
            asset_id=f.asset_id,
            asset_ip=f.asset_ip,
            detected_at=f.detected_at,
            cve_id=f.cve_id,
            cwe_id=f.cwe_id,
            cvss_score=f.cvss_score,
            category=f.category,
            evidence=f.evidence,
            remediation=f.remediation,
            status=f.status,
        )
        for f in filtered_findings
    ]


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get security recommendations based on current findings and device health.

    Recommendations are prioritized by risk reduction potential.
    """
    device_repo = DeviceRepository(db)
    vuln_repo = VulnerabilityRepository(db)
    event_repo = SecurityEventRepository(db)
    correlation_service = SecurityCorrelationService(db)

    # Get all devices
    devices = await device_repo.get_by_user(current_user.id)

    # Collect vulnerabilities and events
    vulnerabilities = []
    events = []
    unhealthy_count = 0
    inactive_count = 0

    for device in devices:
        correlation = await correlation_service.get_device_correlation(device.id, current_user.id)
        if not correlation:
            continue

        if correlation.firewall_enabled is False or correlation.antivirus_enabled is False:
            unhealthy_count += 1

        if correlation.device_status in ["inactive", "stale"]:
            inactive_count += 1

        # Get vulnerabilities
        if correlation.asset_id:
            device_vulns = await vuln_repo.get_by_asset(correlation.asset_id)
            for vuln in device_vulns:
                if vuln.status == "Open":
                    vulnerabilities.append(
                        {
                            "id": vuln.id,
                            "title": vuln.title,
                            "category": vuln.category,
                            "severity": vuln.severity,
                            "device_name": device.name,
                        }
                    )

        # Get events
        device_events = await event_repo.get_by_device(device.id, status="open", limit=100)
        for event in device_events:
            events.append(
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "device_name": device.name,
                }
            )

    # Generate recommendations
    device_health = {
        "unhealthy_devices": unhealthy_count,
        "inactive_devices": inactive_count,
    }

    recommendations = SecurityRecommendationService.generate_recommendations(
        vulnerabilities=vulnerabilities,
        events=events,
        device_health=device_health,
    )

    # Convert to response model
    return [
        RecommendationResponse(
            id=rec.id,
            title=rec.title,
            description=rec.description,
            priority=rec.priority,
            impact=rec.impact,
            effort=rec.effort,
            category=rec.category,
            steps=rec.steps,
            related_findings=rec.related_findings,
            devices_affected=rec.devices_affected,
            estimated_risk_reduction=rec.estimated_risk_reduction,
        )
        for rec in recommendations
    ]
