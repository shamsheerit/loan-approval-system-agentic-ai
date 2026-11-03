from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger
from mcp_servers.risk_rules import RiskRulesServer
from shared.models import RiskAnalysis, LoanApplication
import time

class FinancialRiskAgent:
    def __init__(self):
        self.name = "FinancialRiskAgent"
        self.logger = get_logger(self.name)
        self.mcp_server = RiskRulesServer()

    def analyze(self, application: LoanApplication) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Starting financial risk analysis for {application.applicant_id}")

        try:
            monthly_income = application.applicant_profile.income / 12
            monthly_liabilities = application.existing_liabilities / 12

            dti_response = self.mcp_server.call_tool(
                "calculate_dti_ratio",
                monthly_income=monthly_income,
                monthly_liabilities=monthly_liabilities,
            )
            dti_data = dti_response["result"]
            dti_ratio = dti_data.get("dti_ratio", 0.5)
            dti_classification = dti_data.get("classification", "moderate")

            credit_response = self.mcp_server.call_tool(
                "assess_credit_risk", credit_score=application.credit_score
            )
            credit_data = credit_response["result"]
            credit_risk_level = credit_data.get("risk_level", "fair")
            credit_risk_score = credit_data.get("risk_score", 50)

            loan_response = self.mcp_server.call_tool(
                "evaluate_loan_amount_risk",
                loan_amount=application.loan_amount,
                annual_income=application.applicant_profile.income,
                tenure_months=application.tenure_months,
            )
            loan_data = loan_response["result"]
            loan_to_income = loan_data.get("loan_to_income_ratio", 2)
            loan_amount_risk = loan_data.get("risk_level", "moderate")

            anomaly_response = self.mcp_server.call_tool(
                "detect_anomalies",
                credit_score=application.credit_score,
                dti_ratio=dti_ratio,
                loan_to_income=loan_to_income,
                age=application.applicant_profile.age,
                employment_type=application.applicant_profile.employment_type.value,
            )
            anomaly_data = anomaly_response["result"]
            anomalies = anomaly_data.get("anomalies_detected", [])

            risk_analysis = RiskAnalysis(
                debt_to_income_ratio=dti_ratio,
                credit_score_risk_level=credit_risk_level,
                loan_amount_risk=loan_amount_risk,
                anomalies_detected=anomalies,
                reasoning=self._generate_risk_reasoning(
                    dti_ratio, credit_risk_level, loan_amount_risk, anomalies
                ),
            )

            execution_time_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "agent_name": self.name,
                "output": {
                    **risk_analysis.model_dump(),
                    "credit_risk_score": credit_risk_score,
                    "dti_classification": dti_classification,
                    "anomaly_count": len(anomalies),
                },
                "execution_time_ms": execution_time_ms,
            }

        except Exception as e:
            self.logger.error(f"Error in financial risk analysis: {str(e)}")
            return {
                "status": "error",
                "agent_name": self.name,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

    def _generate_risk_reasoning(
        self,
        dti_ratio: float,
        credit_risk_level: str,
        loan_amount_risk: str,
        anomalies: list,
    ) -> str:
        reasons = []

        if dti_ratio > 0.43:
            reasons.append(f"High DTI ratio of {dti_ratio:.2f}")

        if credit_risk_level in ["poor", "very_poor"]:
            reasons.append(f"Credit risk level: {credit_risk_level}")

        if loan_amount_risk == "very_high":
            reasons.append("Loan amount significantly exceeds income")

        if anomalies:
            reasons.append(f"{len(anomalies)} anomalies detected")

        if not reasons:
            reasons.append("Financial profile within acceptable parameters")

        return "; ".join(reasons)
