"""Security recommendations service for generating actionable remediation guidance."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class SecurityRecommendation:
    """A security recommendation."""

    id: str
    title: str
    description: str
    priority: str  # "critical" | "high" | "medium" | "low"
    impact: str
    effort: str  # "low" | "medium" | "high"
    category: str
    steps: list[str]
    related_findings: list[UUID]
    devices_affected: list[str]
    estimated_risk_reduction: float


class SecurityRecommendationService:
    """
    Service for generating deterministic security recommendations based on findings.

    Recommendations are evidence-based and actionable. They combine:
    - Vulnerability remediation guidance
    - Device health improvements
    - Security event resolution
    - Best practice implementation

    Design principles:
    - Deterministic (no AI/ML inference)
    - Evidence-based (tied to specific findings)
    - Actionable (concrete steps)
    - Prioritized (by risk reduction)
    """

    @staticmethod
    def generate_recommendations(
        vulnerabilities: list[dict],
        events: list[dict],
        device_health: dict,
    ) -> list[SecurityRecommendation]:
        """
        Generate prioritized security recommendations based on current state.

        Args:
            vulnerabilities: List of vulnerability findings
            events: List of security events
            device_health: Device health summary

        Returns:
            List of prioritized recommendations
        """
        recommendations = []

        # Analyze vulnerabilities
        vuln_recommendations = (
            SecurityRecommendationService._generate_vulnerability_recommendations(
                vulnerabilities
            )
        )
        recommendations.extend(vuln_recommendations)

        # Analyze security events
        event_recommendations = (
            SecurityRecommendationService._generate_event_recommendations(events)
        )
        recommendations.extend(event_recommendations)

        # Analyze device health
        health_recommendations = (
            SecurityRecommendationService._generate_health_recommendations(
                device_health
            )
        )
        recommendations.extend(health_recommendations)

        # Sort by priority and risk reduction
        recommendations.sort(
            key=lambda r: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}[r.priority],
                -r.estimated_risk_reduction,
            )
        )

        return recommendations

    @staticmethod
    def _generate_vulnerability_recommendations(
        vulnerabilities: list[dict],
    ) -> list[SecurityRecommendation]:
        """Generate recommendations from vulnerability findings."""
        recommendations = []

        # Group by category
        by_category: dict[str, list[dict]] = {}
        for vuln in vulnerabilities:
            category = vuln.get("category", "Configuration")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(vuln)

        # Cleartext protocol recommendations
        if "Insecure Protocol" in by_category or "Cryptographic Issues" in by_category:
            cleartext_vulns = by_category.get("Insecure Protocol", []) + by_category.get(
                "Cryptographic Issues", []
            )
            if cleartext_vulns:
                recommendations.append(
                    SecurityRecommendation(
                        id="rec_cleartext_protocols",
                        title="Replace Cleartext Protocols with Encrypted Alternatives",
                        description=(
                            "Multiple services are transmitting data without encryption, "
                            "exposing sensitive information to network eavesdropping."
                        ),
                        priority="high",
                        impact="Prevents credential theft and data interception",
                        effort="medium",
                        category="Cryptographic Issues",
                        steps=[
                            "Identify all services using cleartext protocols (Telnet, FTP, HTTP)",
                            "Replace Telnet with SSH for remote administration",
                            "Replace FTP with SFTP or FTPS for file transfers",
                            "Enable HTTPS for all web services with valid SSL/TLS certificates",
                            "Disable cleartext protocols once migration is complete",
                            "Verify encrypted connections with network monitoring",
                        ],
                        related_findings=[vuln["id"] for vuln in cleartext_vulns],
                        devices_affected=list(
                            {vuln.get("device_name", "Unknown") for vuln in cleartext_vulns}
                        ),
                        estimated_risk_reduction=7.5,
                    )
                )

        # Database exposure recommendations
        if "Access Control" in by_category:
            db_vulns = [
                v for v in by_category["Access Control"] if "database" in v.get("title", "").lower()
            ]
            if db_vulns:
                recommendations.append(
                    SecurityRecommendation(
                        id="rec_database_exposure",
                        title="Secure Exposed Database Services",
                        description=(
                            "Database services are accessible over the network without proper isolation. "
                            "This increases the risk of unauthorized data access."
                        ),
                        priority="critical",
                        impact="Prevents unauthorized database access and data breaches",
                        effort="medium",
                        category="Access Control",
                        steps=[
                            "Review database firewall rules and restrict to trusted IPs only",
                            "Enable database authentication with strong passwords or certificates",
                            "Bind databases to localhost if external access is unnecessary",
                            "Enable database audit logging for all access attempts",
                            "Review and minimize database user permissions",
                            "Update database software to latest secure versions",
                            "Consider implementing database encryption at rest",
                        ],
                        related_findings=[vuln["id"] for vuln in db_vulns],
                        devices_affected=list(
                            {vuln.get("device_name", "Unknown") for vuln in db_vulns}
                        ),
                        estimated_risk_reduction=9.0,
                    )
                )

        # Administrative interface recommendations
        if "Access Control" in by_category:
            admin_vulns = [
                v
                for v in by_category["Access Control"]
                if "admin" in v.get("title", "").lower() or "rdp" in v.get("title", "").lower()
            ]
            if admin_vulns:
                recommendations.append(
                    SecurityRecommendation(
                        id="rec_admin_interfaces",
                        title="Harden Administrative Interfaces",
                        description=(
                            "Remote administrative services are exposed to the network. "
                            "These are high-value targets for attackers."
                        ),
                        priority="high",
                        impact="Reduces attack surface for administrative access",
                        effort="low",
                        category="Access Control",
                        steps=[
                            "Restrict administrative service access to trusted IPs via firewall",
                            "Implement VPN requirement for remote administrative access",
                            "Enable multi-factor authentication (MFA) for all admin accounts",
                            "Disable administrative services when not actively needed",
                            "Monitor and alert on all administrative login attempts",
                            "Use SSH key authentication instead of passwords for SSH",
                            "Regularly audit administrative account usage",
                        ],
                        related_findings=[vuln["id"] for vuln in admin_vulns],
                        devices_affected=list(
                            {vuln.get("device_name", "Unknown") for vuln in admin_vulns}
                        ),
                        estimated_risk_reduction=7.0,
                    )
                )

        return recommendations

    @staticmethod
    def _generate_event_recommendations(events: list[dict]) -> list[SecurityRecommendation]:
        """Generate recommendations from security events."""
        recommendations = []

        # Group by event type
        firewall_disabled = [e for e in events if "firewall" in e.get("event_type", "").lower()]
        av_disabled = [e for e in events if "antivirus" in e.get("event_type", "").lower()]

        if firewall_disabled:
            recommendations.append(
                SecurityRecommendation(
                    id="rec_firewall_disabled",
                    title="Enable Firewall Protection on Devices",
                    description=(
                        "Multiple devices have disabled firewalls, leaving them vulnerable "
                        "to network-based attacks."
                    ),
                    priority="high",
                    impact="Prevents unauthorized network access to devices",
                    effort="low",
                    category="Device Security",
                    steps=[
                        "Identify devices with disabled firewalls",
                        "Enable Windows Firewall or host-based firewall on each device",
                        "Configure firewall rules to allow only necessary inbound connections",
                        "Block all inbound connections by default",
                        "Test application connectivity after enabling firewall",
                        "Set up monitoring alerts for firewall status changes",
                    ],
                    related_findings=[e["id"] for e in firewall_disabled],
                    devices_affected=list(
                        {e.get("device_name", "Unknown") for e in firewall_disabled}
                    ),
                    estimated_risk_reduction=6.5,
                )
            )

        if av_disabled:
            recommendations.append(
                SecurityRecommendation(
                    id="rec_antivirus_disabled",
                    title="Enable Antivirus Protection on Devices",
                    description=(
                        "Multiple devices have disabled antivirus protection, increasing "
                        "risk of malware infection."
                    ),
                    priority="high",
                    impact="Prevents malware infections and detects malicious activity",
                    effort="low",
                    category="Device Security",
                    steps=[
                        "Identify devices with disabled antivirus",
                        "Enable Windows Defender or endpoint protection solution",
                        "Update antivirus definitions to latest version",
                        "Run full system scan on each device",
                        "Configure real-time protection and automatic updates",
                        "Set up centralized antivirus monitoring and alerting",
                    ],
                    related_findings=[e["id"] for e in av_disabled],
                    devices_affected=list({e.get("device_name", "Unknown") for e in av_disabled}),
                    estimated_risk_reduction=6.0,
                )
            )

        return recommendations

    @staticmethod
    def _generate_health_recommendations(device_health: dict) -> list[SecurityRecommendation]:
        """Generate recommendations from device health analysis."""
        recommendations = []

        unhealthy_count = device_health.get("unhealthy_devices", 0)
        inactive_count = device_health.get("inactive_devices", 0)

        if unhealthy_count > 0:
            recommendations.append(
                SecurityRecommendation(
                    id="rec_device_health",
                    title="Improve Device Health Monitoring Coverage",
                    description=(
                        f"{unhealthy_count} devices have health issues or stale telemetry. "
                        "Ensure continuous monitoring for security visibility."
                    ),
                    priority="medium",
                    impact="Improves security visibility and incident detection",
                    effort="medium",
                    category="Device Security",
                    steps=[
                        "Verify HORIZON agent is running on all devices",
                        "Check agent connectivity and resolve network issues",
                        "Review agent logs for errors or failures",
                        "Update agents to latest version",
                        "Configure automatic agent restart on failure",
                        "Set up alerting for agent heartbeat failures",
                    ],
                    related_findings=[],
                    devices_affected=[],
                    estimated_risk_reduction=4.0,
                )
            )

        if inactive_count > 3:
            recommendations.append(
                SecurityRecommendation(
                    id="rec_inactive_devices",
                    title="Review and Remove Inactive Devices",
                    description=(
                        f"{inactive_count} devices are inactive or no longer reporting. "
                        "Clean up device inventory to maintain accurate security posture."
                    ),
                    priority="low",
                    impact="Maintains accurate asset inventory and reduces noise",
                    effort="low",
                    category="Device Security",
                    steps=[
                        "Review list of inactive devices",
                        "Verify whether devices are decommissioned or temporarily offline",
                        "Remove decommissioned devices from HORIZON",
                        "Investigate and restore monitoring for temporarily offline devices",
                        "Document device lifecycle and decommissioning process",
                    ],
                    related_findings=[],
                    devices_affected=[],
                    estimated_risk_reduction=1.0,
                )
            )

        return recommendations

    @staticmethod
    def get_recommendation_by_id(
        recommendations: list[SecurityRecommendation], rec_id: str
    ) -> SecurityRecommendation | None:
        """Get a specific recommendation by ID."""
        for rec in recommendations:
            if rec.id == rec_id:
                return rec
        return None
