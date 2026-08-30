import json
import pytest

from app.services.risk_engine import RiskAssessment, RiskEngine


def test_risk_engine_cleartext_protocol():
    assessment = RiskEngine.calculate_risk(
        base_score=5.0,
        factors=["Open HTTP port"],
        port=80,
        is_cleartext=True,
    )

    assert assessment.score == 6.5
    assert assessment.severity == "Medium"
    assert "Transmits credentials/data in cleartext without encryption" in assessment.factors
    assert len(assessment.factors) == 2


def test_risk_engine_database_exposure():
    assessment = RiskEngine.calculate_risk(
        base_score=6.0,
        factors=["Exposed PostgreSQL database"],
        port=5432,
        is_database=True,
    )

    assert assessment.score == 8.0
    assert assessment.severity == "High"
    assert "Database service exposed to network without isolation" in assessment.factors


def test_risk_engine_admin_interface():
    assessment = RiskEngine.calculate_risk(
        base_score=6.5,
        factors=["Exposed RDP service"],
        port=3389,
        is_admin_interface=True,
    )

    assert assessment.score == 8.0
    assert assessment.severity == "High"
    assert "Remote administrative management service exposed" in assessment.factors


def test_risk_engine_critical_threshold():
    assessment = RiskEngine.calculate_risk(
        base_score=8.0,
        factors=["Critical exposure"],
        is_database=True,
    )

    # 8.0 + 2.0 = 10.0 (Critical)
    assert assessment.score == 10.0
    assert assessment.severity == "Critical"


def test_risk_engine_clamping():
    assessment = RiskEngine.calculate_risk(
        base_score=9.5,
        factors=["Extreme risk"],
        is_cleartext=True,
        is_database=True,
        is_admin_interface=True,
    )

    # Score should be capped at 10.0
    assert assessment.score == 10.0
    assert assessment.severity == "Critical"


def test_risk_engine_low_and_info_severities():
    low_assessment = RiskEngine.calculate_risk(
        base_score=2.5,
        factors=["Minor informational notice"],
    )
    assert low_assessment.score == 2.5
    assert low_assessment.severity == "Low"

    info_assessment = RiskEngine.calculate_risk(
        base_score=1.0,
        factors=["Informational service banner"],
    )
    assert info_assessment.score == 1.0
    assert info_assessment.severity == "Info"


def test_risk_engine_factors_json_serialization():
    assessment = RiskEngine.calculate_risk(
        base_score=5.0,
        factors=["Factor 1", "Factor 2"],
        is_cleartext=True,
    )

    factors_data = json.loads(assessment.factors_json)
    assert isinstance(factors_data, list)
    assert len(factors_data) == 3
    assert "Factor 1" in factors_data
