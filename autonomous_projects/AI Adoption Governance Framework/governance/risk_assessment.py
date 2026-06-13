from enum import Enum
from dataclasses import dataclass
from typing import List, Dict

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskAssessment:
    system_name: str
    use_case: str
    data_sensitivity: RiskLevel
    model_transparency: RiskLevel
    impact_if_failed: RiskLevel
    regulatory_requirements: List[str]
    
    def calculate_overall_risk(self) -> RiskLevel:
        """Calculate overall risk based on component risks."""
        risk_values = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        scores = [
            risk_values[self.data_sensitivity],
            risk_values[self.model_transparency],
            risk_values[self.impact_if_failed]
        ]
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 3:
            return RiskLevel.CRITICAL
        elif avg_score >= 2:
            return RiskLevel.HIGH
        elif avg_score >= 1.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_mitigation_recommendations(self) -> List[str]:
        """Get risk-specific mitigation recommendations."""
        recommendations = []
        overall = self.calculate_overall_risk()
        
        if overall in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Implement human-in-the-loop review process")
            recommendations.append("Conduct bias testing across demographic groups")
            recommendations.append("Establish rollback procedures")
        
        if self.data_sensitivity in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Encrypt data at rest and in transit")
            recommendations.append("Implement data retention policies")
            recommendations.append("Avoid third-party model providers for sensitive data")
        
        if self.model_transparency == RiskLevel.CRITICAL:
            recommendations.append("Require explainable AI techniques")
            recommendations.append("Document model decision pathways")
        
        return recommendations

if __name__ == "__main__":
    assessment = RiskAssessment(
        system_name="Loan Approval AI",
        use_case="Automated loan approval decisions",
        data_sensitivity=RiskLevel.HIGH,
        model_transparency=RiskLevel.MEDIUM,
        impact_if_failed=RiskLevel.HIGH,
        regulatory_requirements=["Fair Lending Act", "GDPR"]
    )
    
    print(f"Overall Risk: {assessment.calculate_overall_risk().value}")
    print("Recommendations:")
    for rec in assessment.get_mitigation_recommendations():
        print(f"  - {rec}")
