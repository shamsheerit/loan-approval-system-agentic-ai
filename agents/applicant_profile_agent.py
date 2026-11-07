from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger
from mcp_servers.mcp_provider import MCPServerProvider
from shared.models import ProfileAnalysis, LoanApplication
import time
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

class ApplicantProfileAgent:
    def __init__(self):
        self.name = "ApplicantProfileAgent"
        self.logger = get_logger(self.name)
        self.mcp_provider = MCPServerProvider.get_instance()
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url=os.getenv("ANTHROPIC_BASE_URL")
        )

    def analyze(self, application: LoanApplication) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Starting profile analysis for {application.applicant_id}")

        try:
            employment_type = application.applicant_profile.employment_type

            income_stability_score = self._calculate_income_stability(employment_type)
            employment_risk = self._assess_employment_risk(employment_type, income_stability_score)

            profile_info = {
                "applicant_id": application.applicant_id,
                "age": application.applicant_profile.age,
                "income": application.applicant_profile.income,
                "employment_type": employment_type.value,
                "credit_history": "Sourced from form input",
                "employment_history": f"{employment_type.value.replace('_', ' ').title()} since unknown date",
            }

            completeness_flags = []
            if not application.applicant_id:
                completeness_flags.append("Missing applicant ID")

            llm_assessment = self._get_llm_profile_assessment(
                application, income_stability_score, employment_risk, profile_info
            )

            profile_analysis = ProfileAnalysis(
                income_stability_score=income_stability_score,
                employment_risk=employment_risk,
                credit_history_summary="Form-based profile assessment",
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

    def _calculate_income_stability(self, employment_type) -> float:
        from shared.models import EmploymentType
        if employment_type == EmploymentType.SALARIED:
            return 85.0
        elif employment_type == EmploymentType.BUSINESS:
            return 65.0
        elif employment_type == EmploymentType.SELF_EMPLOYED:
            return 60.0
        return 60.0

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
                model=os.getenv("ANTHROPIC_BASE_MODEL", "global.anthropic.claude-haiku-4-5-20251001-v1:0"),
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            self.logger.warning(f"LLM assessment failed: {str(e)}")
            return f"Employment risk: {employment_risk}, Income stability: {income_stability_score}/100"
