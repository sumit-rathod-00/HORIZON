"""Security prioritization service for ranking and filtering findings."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PrioritizedFinding:
    """A prioritized security finding."""

    id: UUID
    type: str  # "vulnerability" | "event"
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


class SecurityPrioritizationService:
    """
    Service for prioritizing security findings across vulnerabilities and events.

    Priority calculation factors:
    - Severity (Critical > High > Medium > Low > Info)
    - Risk score (vulnerability risk or calculated event risk)
    - CVSS score (when available)
    - Device health context (firewall/AV disabled)
    - Time sensitivity (recent detections)
    - Asset criticality (database/admin services)
    """

    # Severity weights
    SEVERITY_WEIGHTS = {
        "critical": 10.0,
        "Critical": 10.0,
        "high": 7.5,
        "High": 7.5,
        "medium": 5.0,
        "Medium": 5.0,
        "low": 2.5,
        "Low": 2.5,
        "info": 1.0,
        "Info": 1.0,
    }

    @staticmethod
    def calculate_priority_score(
        severity: str,
        risk_score: float | None,
        cvss_score: float | None,
        category: str | None,
        detected_at: datetime,
        device_unhealthy: bool = False,
    ) -> float:
        """
        Calculate priority score (0-100).

        Higher score = higher priority.

        Factors:
        - Severity weight (0-10)
        - Risk score (0-10)
        - CVSS score (0-10)
        - Category multiplier (crypto/auth issues get boost)
        - Recency bonus (recent detections)
        - Device health penalty (unhealthy devices increase priority)
        """
        score = 0.0

        # Base severity weight (40% of total)
        severity_weight = SecurityPrioritizationService.SEVERITY_WEIGHTS.get(
            severity, 2.5
        )
        score += severity_weight * 4.0

        # Risk score (30% of total)
        if risk_score:
            score += min(risk_score, 10.0) * 3.0

        # CVSS score (20% of total)
        if cvss_score:
            score += min(cvss_score, 10.0) * 2.0

        # Category multiplier (10% of total)
        category_bonus = 0.0
        if category:
            category_lower = category.lower()
            if "crypto" in category_lower or "authentication" in category_lower:
                category_bonus = 10.0
            elif "access control" in category_lower:
                category_bonus = 7.5
            elif "configuration" in category_lower:
                category_bonus = 2.5

        score += category_bonus

        # Recency bonus (up to +15)
        now = datetime.now(detected_at.tzinfo or None)
        hours_old = (now - detected_at).total_seconds() / 3600
        if hours_old < 1:
            score += 15.0
        elif hours_old < 24:
            score += 10.0
        elif hours_old < 168:  # 1 week
            score += 5.0

        # Device health penalty (up to +10)
        if device_unhealthy:
            score += 10.0

        return min(round(score, 1), 100.0)

    @staticmethod
    def filter_by_priority(
        findings: list[PrioritizedFinding],
        min_priority: float | None = None,
        severity_filter: list[str] | None = None,
        category_filter: list[str] | None = None,
        limit: int | None = None,
    ) -> list[PrioritizedFinding]:
        """
        Filter and sort prioritized findings.

        Args:
            findings: List of prioritized findings
            min_priority: Minimum priority score threshold
            severity_filter: Filter by severity (e.g., ["Critical", "High"])
            category_filter: Filter by category (e.g., ["Cryptographic Issues"])
            limit: Maximum number of results

        Returns:
            Filtered and sorted findings (highest priority first)
        """
        filtered = findings

        # Apply filters
        if min_priority is not None:
            filtered = [f for f in filtered if f.priority_score >= min_priority]

        if severity_filter:
            severity_set = {s.lower() for s in severity_filter}
            filtered = [f for f in filtered if f.severity.lower() in severity_set]

        if category_filter:
            category_set = {c.lower() for c in category_filter}
            filtered = [
                f
                for f in filtered
                if f.category and f.category.lower() in category_set
            ]

        # Sort by priority (highest first)
        sorted_findings = sorted(
            filtered, key=lambda f: f.priority_score, reverse=True
        )

        # Apply limit
        if limit:
            sorted_findings = sorted_findings[:limit]

        return sorted_findings

    @staticmethod
    def group_by_severity(
        findings: list[PrioritizedFinding],
    ) -> dict[str, list[PrioritizedFinding]]:
        """Group findings by severity level."""
        groups: dict[str, list[PrioritizedFinding]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": [],
        }

        for finding in findings:
            severity_key = finding.severity.lower()
            if severity_key in groups:
                groups[severity_key].append(finding)

        return groups

    @staticmethod
    def group_by_device(
        findings: list[PrioritizedFinding],
    ) -> dict[str, list[PrioritizedFinding]]:
        """Group findings by device."""
        groups: dict[str, list[PrioritizedFinding]] = {}

        for finding in findings:
            device_key = finding.device_name or "Unknown Device"
            if device_key not in groups:
                groups[device_key] = []
            groups[device_key].append(finding)

        return groups

    @staticmethod
    def get_top_priorities(
        findings: list[PrioritizedFinding], count: int = 10
    ) -> list[PrioritizedFinding]:
        """Get top N highest priority findings."""
        return SecurityPrioritizationService.filter_by_priority(
            findings, limit=count
        )
