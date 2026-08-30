"""AI and Security Analysis Provider Abstraction Layer for HORIZON."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SecurityInsight:
    summary: str
    business_impact: str
    remediation_advice: str
    confidence: float
    provider_name: str


class AISecurityProvider(ABC):
    """Abstract interface for AI security analysis and explanation providers."""

    @abstractmethod
    async def explain_vulnerability(
        self,
        title: str,
        description: str | None,
        severity: str,
        evidence: str | None,
        context: dict[str, Any] | None = None,
    ) -> SecurityInsight:
        """Provide a business-friendly explanation and remediation for a vulnerability."""
        raise NotImplementedError
