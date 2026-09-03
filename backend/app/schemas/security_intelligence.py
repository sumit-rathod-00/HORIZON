"""Security intelligence schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RiskSummaryResponse(BaseModel):
    """Organization-wide risk summary."""

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


class CorrelationResponse(BaseModel):
    """Correlated security data for a device."""

    device_id: UUID
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


class PrioritizedFindingResponse(BaseModel):
    """A prioritized security finding."""

    id: UUID
    type: str = Field(description="vulnerability or event")
    title: str
    description: str
    severity: str
    risk_score: float
    priority_score: float
    device_id: UUID | None
    device_name: str | None
    asset_id: UUID | None
    asset_ip: str | None
    detected_at: datetime
    cve_id: str | None = None
    cwe_id: str | None = None
    cvss_score: float | None = None
    category: str | None = None
    evidence: str | None = None
    remediation: str | None = None
    status: str | None = None


class RecommendationResponse(BaseModel):
    """A security recommendation."""

    id: str
    title: str
    description: str
    priority: str
    impact: str
    effort: str
    category: str
    steps: list[str]
    related_findings: list[UUID]
    devices_affected: list[str]
    estimated_risk_reduction: float
