"""FastMCP-based agent communication servers"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Server
import asyncio
from typing import Dict, Any
from shared.utils import get_logger
from mcp_servers.applicant_db import ApplicantDBServer
from mcp_servers.risk_rules import RiskRulesServer
from mcp_servers.decision_synthesis import DecisionSynthesisServer
from mcp_servers.notification_system import NotificationSystemServer

logger = get_logger("FastMCPServers")


class MCPAgentServer:
    """Unified MCP server for all agent tools"""

    def __init__(self):
        self.server = Server("loan-approval-agents")
        self.applicant_db = ApplicantDBServer()
        self.risk_rules = RiskRulesServer()
        self.decision_synthesis = DecisionSynthesisServer()
        self.notification_system = NotificationSystemServer()
        self._register_tools()

    def _register_tools(self):
        """Register all tools from MCP servers"""

        @self.server.call_tool()
        async def fetch_applicant_profile(applicant_id: str) -> Dict[str, Any]:
            """Fetch applicant profile from database"""
            return self.applicant_db.fetch_applicant_profile(applicant_id)

        @self.server.call_tool()
        async def get_income_stability_score(applicant_id: str) -> Dict[str, Any]:
            """Get income stability score"""
            return self.applicant_db.get_income_stability_score(applicant_id)

        @self.server.call_tool()
        async def validate_application_completeness(applicant_id: str) -> Dict[str, Any]:
            """Validate application completeness"""
            return self.applicant_db.validate_application_completeness(applicant_id)

        @self.server.call_tool()
        async def calculate_dti_ratio(
            monthly_income: float, monthly_liabilities: float
        ) -> Dict[str, Any]:
            """Calculate debt-to-income ratio"""
            return self.risk_rules.calculate_dti_ratio(
                monthly_income, monthly_liabilities
            )

        @self.server.call_tool()
        async def assess_credit_risk(credit_score: int) -> Dict[str, Any]:
            """Assess credit risk"""
            return self.risk_rules.assess_credit_risk(credit_score)

        @self.server.call_tool()
        async def evaluate_loan_amount_risk(
            loan_amount: float, annual_income: float, tenure_months: int
        ) -> Dict[str, Any]:
            """Evaluate loan amount risk"""
            return self.risk_rules.evaluate_loan_amount_risk(
                loan_amount, annual_income, tenure_months
            )

        @self.server.call_tool()
        async def detect_anomalies(
            credit_score: int,
            dti_ratio: float,
            loan_to_income: float,
            age: int,
            employment_type: str,
        ) -> Dict[str, Any]:
            """Detect anomalies in applicant profile"""
            return self.risk_rules.detect_anomalies(
                credit_score, dti_ratio, loan_to_income, age, employment_type
            )

        @self.server.call_tool()
        async def synthesize_decision(
            profile_analysis: Dict[str, Any], risk_analysis: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Synthesize loan decision"""
            return self.decision_synthesis.synthesize_decision(
                profile_analysis, risk_analysis
            )

        @self.server.call_tool()
        async def send_notification(
            case_id: str, decision: str, applicant_email: str = "applicant@example.com"
        ) -> Dict[str, Any]:
            """Send decision notification"""
            return self.notification_system.send_notification(
                case_id, decision, applicant_email
            )

        @self.server.call_tool()
        async def log_case(
            case_id: str,
            decision: str,
            risk_score: float,
            decision_factors: list,
            applicant_id: str = "unknown",
        ) -> Dict[str, Any]:
            """Log case in audit trail"""
            return self.notification_system.log_case(
                case_id, decision, risk_score, decision_factors, applicant_id
            )

        @self.server.call_tool()
        async def get_case_history(limit: int = 10) -> Dict[str, Any]:
            """Get case history"""
            return self.notification_system.get_case_history(limit)

    async def run(self, host: str = "localhost", port: int = 3001):
        """Run the MCP server"""
        logger.info(f"Starting FastMCP agent server on {host}:{port}")
        await self.server.run(host, port)


if __name__ == "__main__":
    server = MCPAgentServer()
    asyncio.run(server.run())
