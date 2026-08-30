"""Deterministic implementation of AISecurityProvider that requires no paid API."""
from __future__ import annotations

from typing import Any

from app.services.ai.base import AISecurityProvider, SecurityInsight


class DeterministicSecurityProvider(AISecurityProvider):
    """Deterministic security analyzer that generates consistent, explainable insights locally."""

    async def explain_vulnerability(
        self,
        title: str,
        description: str | None,
        severity: str,
        evidence: str | None,
        context: dict[str, Any] | None = None,
    ) -> SecurityInsight:
        summary = f"Identified security finding: {title} (Severity: {severity})"

        if severity in ("Critical", "High"):
            business_impact = (
                "High risk of unauthorized network exposure or data interception. "
                "Immediate remediation is recommended to reduce exposure surface."
            )
        elif severity == "Medium":
            business_impact = (
                "Moderate exposure risk. If unmanaged, this service could be leveraged "
                "by an attacker for reconnaissance or lateral movement."
            )
        else:
            business_impact = (
                "Low to informational exposure. Minimal immediate threat, "
                "but recommended to adhere to principle of least privilege."
            )

        remediation_advice = (
            "1. Restrict network exposure using firewall rules.\n"
            "2. Ensure strong authentication and patch versions.\n"
            "3. Enforce encrypted protocols (TLS/SSH) where applicable."
        )

        return SecurityInsight(
            summary=summary,
            business_impact=business_impact,
            remediation_advice=remediation_advice,
            confidence=1.0,
            provider_name="deterministic_rule_engine",
        )
