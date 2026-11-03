from .base_server import BaseMCPServer
from typing import Dict, Any, List

class RiskRulesServer(BaseMCPServer):
    def __init__(self):
        self.credit_score_thresholds = {
            "excellent": (750, 850),
            "good": (700, 749),
            "fair": (650, 699),
            "poor": (600, 649),
            "very_poor": (300, 599),
        }
        self.dti_thresholds = {
            "low": (0, 0.30),
            "moderate": (0.30, 0.43),
            "high": (0.43, 0.50),
            "very_high": (0.50, float("inf")),
        }
        super().__init__("RiskRulesServer")

    def _register_tools(self):
        self.tools["calculate_dti_ratio"] = self.calculate_dti_ratio
        self.tools["assess_credit_risk"] = self.assess_credit_risk
        self.tools["evaluate_loan_amount_risk"] = self.evaluate_loan_amount_risk
        self.tools["detect_anomalies"] = self.detect_anomalies

    def calculate_dti_ratio(
        self, monthly_income: float, monthly_liabilities: float
    ) -> Dict[str, Any]:
        if monthly_income <= 0:
            return {"error": "Monthly income must be positive"}

        dti = monthly_liabilities / monthly_income
        classification = self._classify_dti(dti)

        return {
            "dti_ratio": round(dti, 2),
            "classification": classification,
            "monthly_income": monthly_income,
            "monthly_liabilities": monthly_liabilities,
        }

    def assess_credit_risk(self, credit_score: int) -> Dict[str, Any]:
        risk_level = "unknown"
        risk_score = 50

        for level, (min_score, max_score) in self.credit_score_thresholds.items():
            if min_score <= credit_score <= max_score:
                risk_level = level
                if level == "excellent":
                    risk_score = 10
                elif level == "good":
                    risk_score = 25
                elif level == "fair":
                    risk_score = 50
                elif level == "poor":
                    risk_score = 75
                elif level == "very_poor":
                    risk_score = 90
                break

        return {
            "credit_score": credit_score,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendation": self._get_credit_recommendation(risk_level),
        }

    def evaluate_loan_amount_risk(
        self, loan_amount: float, annual_income: float, tenure_months: int
    ) -> Dict[str, Any]:
        if annual_income <= 0:
            return {"error": "Annual income must be positive"}

        loan_to_income = loan_amount / annual_income
        monthly_payment = (loan_amount / tenure_months) * 1.05

        risk_level = "low"
        if loan_to_income > 5:
            risk_level = "very_high"
        elif loan_to_income > 3:
            risk_level = "high"
        elif loan_to_income > 1.5:
            risk_level = "moderate"

        return {
            "loan_amount": loan_amount,
            "annual_income": annual_income,
            "loan_to_income_ratio": round(loan_to_income, 2),
            "estimated_monthly_payment": round(monthly_payment, 2),
            "risk_level": risk_level,
        }

    def detect_anomalies(
        self,
        credit_score: int,
        dti_ratio: float,
        loan_to_income: float,
        age: int,
        employment_type: str,
    ) -> Dict[str, Any]:
        anomalies: List[str] = []

        if credit_score < 500 and dti_ratio > 0.5:
            anomalies.append("High-risk profile: Low credit score with high DTI")

        if loan_to_income > 4:
            anomalies.append("Loan amount significantly exceeds annual income")

        if age < 25 and loan_to_income > 2:
            anomalies.append("Young applicant with high loan-to-income ratio")

        if employment_type == "self_employed" and credit_score < 650:
            anomalies.append("Self-employed with below-average credit score")

        return {
            "anomalies_detected": anomalies,
            "anomaly_count": len(anomalies),
            "overall_risk": "high" if len(anomalies) > 2 else "normal",
        }

    def _classify_dti(self, dti: float) -> str:
        for classification, (min_val, max_val) in self.dti_thresholds.items():
            if min_val <= dti <= max_val:
                return classification
        return "unknown"

    def _get_credit_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "excellent": "Approve with preferential rates",
            "good": "Approve with standard rates",
            "fair": "Review with additional verification",
            "poor": "Consider rejection or require collateral",
            "very_poor": "Reject or require co-signer",
        }
        return recommendations.get(risk_level, "Review required")
