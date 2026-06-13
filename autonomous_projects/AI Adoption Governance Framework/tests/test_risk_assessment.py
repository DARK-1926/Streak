import pytest
from governance.risk_assessment import RiskAssessment, RiskLevel

def test_low_risk_calculation():
    """Test that low-risk systems are correctly identified."""
    assessment = RiskAssessment(
        system_name="Product Recommendation",
        use_case="Suggest products to users",
        data_sensitivity=RiskLevel.LOW,
        model_transparency=RiskLevel.LOW,
        impact_if_failed=RiskLevel.LOW,
        regulatory_requirements=[]
    )
    assert assessment.calculate_overall_risk() == RiskLevel.LOW

def test_high_risk_calculation():
    """Test that high-risk systems are correctly identified."""
    assessment = RiskAssessment(
        system_name="Medical Diagnosis AI",
        use_case="Diagnose medical conditions",
        data_sensitivity=RiskLevel.HIGH,
        model_transparency=RiskLevel.HIGH,
        impact_if_failed=RiskLevel.CRITICAL,
        regulatory_requirements=["HIPAA", "FDA"]
    )
    assert assessment.calculate_overall_risk() == RiskLevel.CRITICAL

def test_mitigation_recommendations():
    """Test that mitigation recommendations are generated."""
    assessment = RiskAssessment(
        system_name="Financial Trading AI",
        use_case="Execute trades based on market predictions",
        data_sensitivity=RiskLevel.HIGH,
        model_transparency=RiskLevel.MEDIUM,
        impact_if_failed=RiskLevel.HIGH,
        regulatory_requirements=["SEC"]
    )
    recommendations = assessment.get_mitigation_recommendations()
    assert len(recommendations) > 0
    assert any("human-in-the-loop" in rec for rec in recommendations)

def test_medium_risk_system():
    """Test medium risk system assessment."""
    assessment = RiskAssessment(
        system_name="Customer Support Chatbot",
        use_case="Answer customer questions",
        data_sensitivity=RiskLevel.MEDIUM,
        model_transparency=RiskLevel.LOW,
        impact_if_failed=RiskLevel.MEDIUM,
        regulatory_requirements=[]
    )
    risk = assessment.calculate_overall_risk()
    assert risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]
