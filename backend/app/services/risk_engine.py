from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    severity: str
    factors: list[str]

    @property
    def factors_json(self) -> str:
        return json.dumps(self.factors)


class RiskEngine:
    """Deterministic, explainable risk scoring engine for network findings."""

    @staticmethod
    def calculate_risk(
        base_score: float,
        factors: list[str],
        port: int | None = None,
        service: str | None = None,
        is_cleartext: bool = False,
        is_database: bool = False,
        is_admin_interface: bool = False,
        # Layer 3: Contextual risk factors
        device_status: str | None = None,
        firewall_enabled: bool | None = None,
        antivirus_enabled: bool | None = None,
        event_severity: str | None = None,
        exposure_public: bool = False,
    ) -> RiskAssessment:
        score = base_score
        calculated_factors = list(factors)

        if is_cleartext:
            score += 1.5
            calculated_factors.append("Transmits credentials/data in cleartext without encryption")

        if is_database:
            score += 2.0
            calculated_factors.append("Database service exposed to network without isolation")

        if is_admin_interface:
            score += 1.5
            calculated_factors.append("Remote administrative management service exposed")

        # Layer 3: Device health context
        if firewall_enabled is False:
            score += 1.0
            calculated_factors.append("Device firewall is disabled")

        if antivirus_enabled is False:
            score += 0.5
            calculated_factors.append("Device antivirus protection is disabled")

        if device_status in ["inactive", "stale"]:
            score += 0.5
            calculated_factors.append(f"Device is {device_status} (monitoring unavailable)")

        # Layer 3: Exposure context
        if exposure_public:
            score += 1.5
            calculated_factors.append("Service exposed to public internet")

        # Layer 3: Security event severity context
        if event_severity in ["critical", "high"]:
            score += 1.0
            calculated_factors.append(f"Associated with {event_severity} severity security event")

        # Clamp between 0.0 and 10.0
        score = min(10.0, max(0.0, round(score, 1)))

        # Determine severity category from score
        if score >= 9.0:
            severity = "Critical"
        elif score >= 7.0:
            severity = "High"
        elif score >= 4.0:
            severity = "Medium"
        elif score >= 2.0:
            severity = "Low"
        else:
            severity = "Info"

        return RiskAssessment(
            score=score,
            severity=severity,
            factors=calculated_factors,
        )
