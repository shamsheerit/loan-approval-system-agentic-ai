from .base_server import BaseMCPServer
from typing import Dict, Any
from shared.models import DecisionClassification

class DecisionSynthesisServer(BaseMCPServer):
    def __init__(self):
        super().__init__("DecisionSynthesisServer")

    def _register_tools(self):
        self.tools["synthesize_decision"] = self.synthesize_decision

    def synthesize_decision(
        self,
        profile_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        income_stability = profile_analysis.get("income_stability_score", 50)
        dti_ratio = risk_analysis.get("dti_ratio", 0.5)
        credit_risk_score = risk_analysis.get("credit_risk_score", 50)
        anomaly_count = risk_analysis.get("anomaly_count", 0)

        combined_risk_score = (
            (credit_risk_score * 0.45)
            + ((dti_ratio * 100) * 0.35)
            + ((100 - income_stability) * 0.2)
        )

        combined_risk_score = min(100, max(0, combined_risk_score))

        # Boost risk score for extreme anomalies
        if anomaly_count >= 4:
            combined_risk_score = min(100, combined_risk_score + 25)
        elif anomaly_count >= 3:
            combined_risk_score = min(100, combined_risk_score + 15)

        classification = self._determine_classification(
            combined_risk_score, anomaly_count
        )
        confidence = self._calculate_confidence(
            combined_risk_score, income_stability, anomaly_count
        )

        decision_factors = self._extract_decision_factors(
            profile_analysis, risk_analysis, anomaly_count
        )
        explanation = self._generate_explanation(
            classification, combined_risk_score, decision_factors
        )

        return {
            "classification": classification.value,
            "risk_score": round(combined_risk_score, 2),
            "confidence_level": round(confidence, 2),
            "decision_factors": decision_factors,
            "explanation": explanation,
        }

    def _determine_classification(
        self, risk_score: float, anomaly_count: int
    ) -> DecisionClassification:
        # High risk score always triggers rejection, even with anomalies
        if risk_score >= 75:
            return DecisionClassification.REJECTED

        # Multiple anomalies with high risk triggers manual review
        if anomaly_count >= 3 and risk_score >= 60:
            return DecisionClassification.MANUAL_REVIEW

        # Standard classification by risk score
        if risk_score >= 70:
            return DecisionClassification.REJECTED
        elif risk_score >= 40:
            return DecisionClassification.MANUAL_REVIEW
        else:
            return DecisionClassification.APPROVED

    def _calculate_confidence(
        self, risk_score: float, income_stability: float, anomaly_count: int
    ) -> float:
        base_confidence = 0.85
        risk_adjustment = abs(risk_score - 50) / 100
        stability_adjustment = income_stability / 100
        anomaly_adjustment = max(0, 1 - (anomaly_count * 0.15))

        confidence = base_confidence * stability_adjustment * anomaly_adjustment

        if 35 <= risk_score <= 65:
            confidence *= 0.7

        return min(1.0, max(0.0, confidence))

    def _extract_decision_factors(
        self,
        profile_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        anomaly_count: int,
    ) -> list:
        factors = []

        income_stability = profile_analysis.get("income_stability_score", 50)
        if income_stability > 75:
            factors.append("Strong income stability")
        elif income_stability < 50:
            factors.append("Weak income stability")

        dti_ratio = risk_analysis.get("dti_ratio", 0.5)
        if dti_ratio < 0.3:
            factors.append("Favorable debt-to-income ratio")
        elif dti_ratio > 0.43:
            factors.append("High debt-to-income ratio")

        credit_risk = risk_analysis.get("credit_risk_level", "fair")
        if credit_risk in ["excellent", "good"]:
            factors.append("Good credit profile")
        elif credit_risk in ["poor", "very_poor"]:
            factors.append("Poor credit profile")

        if anomaly_count > 0:
            factors.append(f"{anomaly_count} potential risk anomalies detected")

        return factors

    def _generate_explanation(
        self,
        classification: DecisionClassification,
        risk_score: float,
        decision_factors: list,
    ) -> str:
        if classification == DecisionClassification.APPROVED:
            return (
                f"Application approved. Risk assessment score: {risk_score:.1f}/100 "
                f"(Low risk). Key factors: {', '.join(decision_factors[:2])}"
            )
        elif classification == DecisionClassification.REJECTED:
            return (
                f"Application rejected. Risk assessment score: {risk_score:.1f}/100 "
                f"(High risk). Key factors: {', '.join(decision_factors[:2])}"
            )
        else:
            return (
                f"Application requires manual review. Risk assessment score: {risk_score:.1f}/100 "
                f"(Moderate risk). Key factors: {', '.join(decision_factors)}"
            )
