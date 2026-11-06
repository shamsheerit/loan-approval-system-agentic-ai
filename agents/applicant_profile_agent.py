from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger
from mcp_servers.applicant_db import ApplicantDBServer
from shared.models import ProfileAnalysis, LoanApplication
import time
import anthropic
import json

class ApplicantProfileAgent:
    def __init__(self):
        self.name = "ApplicantProfileAgent"
        self.logger = get_logger(self.name)
        self.mcp_server = ApplicantDBServer()
        self.client = anthropic.Anthropic()

    def analyze(self, application: LoanApplication) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Starting profile analysis for {application.applicant_id}")

        try:
            profile_data = self.mcp_server.call_tool(
                "fetch_applicant_profile", applicant_id=application.applicant_id
            )

            if profile_data["status"] == "error":
                return {
                    "status": "error",
                    "agent_name": self.name,
                    "error": profile_data.get("error", "Unknown error"),
                }

            profile_info = profile_data["result"]

            income_stability_response = self.mcp_server.call_tool(
                "get_income_stability_score", applicant_id=application.applicant_id
            )

            income_stability_score = income_stability_response["result"].get(
                "income_stability_score", 60
            )

            employment_risk = self._assess_employment_risk(
                application.applicant_profile.employment_type,
                income_stability_score,
            )

            completeness_response = self.mcp_server.call_tool(
                "validate_application_completeness", applicant_id=application.applicant_id
            )

            completeness_flags = completeness_response["result"].get("flags", [])

            llm_assessment = self._get_llm_profile_assessment(
                application, income_stability_score, employment_risk, profile_info
            )

            profile_analysis = ProfileAnalysis(
                income_stability_score=income_stability_score,
                employment_risk=employment_risk,
                credit_history_summary=profile_info.get(
                    "credit_history", "No history available"
                ),
                application_completeness_flags=completeness_flags,
                llm_assessment=llm_assessment,
            )

            execution_time_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "agent_name": self.name,
                "output": profile_analysis.model_dump(),
                "execution_time_ms": execution_time_ms,
            }

        except Exception as e:
            self.logger.error(f"Error in profile analysis: {str(e)}")
            return {
                "status": "error",
                "agent_name": self.name,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

    def _assess_employment_risk(
        self, employment_type: str, income_stability_score: float
    ) -> str:
        if income_stability_score >= 80:
            return "low"
        elif income_stability_score >= 60:
            return "moderate"
        else:
            return "high"

    def _get_llm_profile_assessment(
        self,
        application: LoanApplication,
        income_stability_score: float,
        employment_risk: str,
        profile_info: Dict[str, Any],
    ) -> str:
        try:
            prompt = f"""You are a loan profile analyst. Assess this applicant's profile:

Age: {application.applicant_profile.age}
Annual Income: ${application.applicant_profile.income:,.0f}
Employment Type: {application.applicant_profile.employment_type.value}
Income Stability Score: {income_stability_score}/100
Employment Risk Level: {employment_risk}
Credit History: {profile_info.get('credit_history', 'Unknown')}
Employment History: {profile_info.get('employment_history', 'Unknown')}

Provide a concise 2-3 sentence assessment of the applicant's profile strength and any concerns."""

            message = self.client.messages.create(
                model="claude-opus-4-1",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            self.logger.warning(f"LLM assessment failed: {str(e)}")
            return f"Employment risk: {employment_risk}, Income stability: {income_stability_score}/100"
