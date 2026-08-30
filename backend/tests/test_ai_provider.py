import pytest

from app.services.ai.deterministic_analyzer import DeterministicSecurityProvider


@pytest.mark.asyncio
async def test_deterministic_provider_critical_severity():
    provider = DeterministicSecurityProvider()

    insight = await provider.explain_vulnerability(
        title="Remote Code Execution",
        description="Critical RCE vulnerability",
        severity="Critical",
        evidence="CVE-2024-1234",
    )

    assert insight.summary is not None
    assert "Critical RCE vulnerability" not in insight.summary  # Should not echo input
    assert "Remote Code Execution" in insight.summary
    assert "Critical" in insight.summary
    assert insight.business_impact is not None
    assert "High risk" in insight.business_impact or "Immediate" in insight.business_impact
    assert insight.remediation_advice is not None
    assert insight.confidence == 1.0
    assert insight.provider_name == "deterministic_rule_engine"


@pytest.mark.asyncio
async def test_deterministic_provider_medium_severity():
    provider = DeterministicSecurityProvider()

    insight = await provider.explain_vulnerability(
        title="Exposed HTTP Service",
        description="HTTP without encryption",
        severity="Medium",
        evidence="Port 80 open",
    )

    assert "Medium" in insight.summary
    assert "Moderate" in insight.business_impact
    assert insight.confidence == 1.0


@pytest.mark.asyncio
async def test_deterministic_provider_low_severity():
    provider = DeterministicSecurityProvider()

    insight = await provider.explain_vulnerability(
        title="Service Banner Disclosure",
        description="Version information exposed",
        severity="Low",
        evidence="Apache 2.4.41",
    )

    assert "Low" in insight.summary
    assert "Low to informational" in insight.business_impact
    assert insight.confidence == 1.0


@pytest.mark.asyncio
async def test_deterministic_provider_with_context():
    provider = DeterministicSecurityProvider()

    insight = await provider.explain_vulnerability(
        title="Database Exposed",
        description="PostgreSQL accessible",
        severity="High",
        evidence="Port 5432 open",
        context={"port": 5432, "service": "postgresql"},
    )

    assert "High" in insight.summary
    assert insight.business_impact is not None
    assert insight.remediation_advice is not None
