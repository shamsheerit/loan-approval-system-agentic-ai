from .base_server import BaseMCPServer
from typing import Dict, Any
from shared.models import ApplicantProfile, EmploymentType

class ApplicantDBServer(BaseMCPServer):
    def __init__(self):
        self.mock_applicants = {
            "APP001": {
                "profile": ApplicantProfile(
                    age=35, income=60000, employment_type=EmploymentType.SALARIED
                ),
                "credit_history": "No defaults, 5 years credit history",
                "employment_history": "Employed since 2015",
            },
            "APP002": {
                "profile": ApplicantProfile(
                    age=45, income=120000, employment_type=EmploymentType.BUSINESS
                ),
                "credit_history": "One missed payment 2 years ago",
                "employment_history": "Self-employed since 2010",
            },
            "APP003": {
                "profile": ApplicantProfile(
                    age=28, income=35000, employment_type=EmploymentType.SELF_EMPLOYED
                ),
                "credit_history": "Limited credit history, new applicant",
                "employment_history": "Self-employed since 2021",
            },
        }
        super().__init__("ApplicantDBServer")

    def _register_tools(self):
        self.tools["fetch_applicant_profile"] = self.fetch_applicant_profile
        self.tools["validate_application_completeness"] = (
            self.validate_application_completeness
        )
        self.tools["get_income_stability_score"] = self.get_income_stability_score

    def fetch_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        if applicant_id in self.mock_applicants:
            data = self.mock_applicants[applicant_id]
            return {
                "applicant_id": applicant_id,
                "profile": data["profile"].model_dump(),
                "credit_history": data["credit_history"],
                "employment_history": data["employment_history"],
            }
        return {"error": f"Applicant {applicant_id} not found"}

    def validate_application_completeness(
        self, applicant_id: str
    ) -> Dict[str, Any]:
        flags = []
        if applicant_id not in self.mock_applicants:
            flags.append("Applicant not found")
        return {
            "applicant_id": applicant_id,
            "is_complete": len(flags) == 0,
            "flags": flags,
        }

    def get_income_stability_score(self, applicant_id: str) -> Dict[str, Any]:
        if applicant_id not in self.mock_applicants:
            return {"error": f"Applicant {applicant_id} not found"}

        data = self.mock_applicants[applicant_id]
        profile = data["profile"]
        employment_type = profile.employment_type

        base_score = 60
        if employment_type == EmploymentType.SALARIED:
            base_score = 85
        elif employment_type == EmploymentType.BUSINESS:
            base_score = 65
        elif employment_type == EmploymentType.SELF_EMPLOYED:
            base_score = 60

        return {
            "applicant_id": applicant_id,
            "income_stability_score": min(100, base_score),
            "employment_type": employment_type,
        }
