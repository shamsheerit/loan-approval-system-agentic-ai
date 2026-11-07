from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger, generate_case_id
from mcp_servers.mcp_provider import MCPServerProvider
import time

class ComplianceOrchestratorAgent:
    def __init__(self):
        self.name = "ComplianceOrchestratorAgent"
        self.logger = get_logger(self.name)
        self.mcp_provider = MCPServerProvider.get_instance()

    def execute(
        self,
        decision: Dict[str, Any],
        applicant_id: str,
        applicant_email: str = "applicant@example.com",
    ) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Executing compliance actions for {applicant_id}")

        try:
            case_id = decision.get("case_id", generate_case_id())

            log_response = self.mcp_provider.call_tool(
                "notification_system", "log_case",
                case_id=case_id,
                decision=decision.get("classification", "UNKNOWN"),
                risk_score=decision.get("risk_score", 0),
                decision_factors=decision.get("decision_factors", []),
                applicant_id=applicant_id,
            )

            if log_response["status"] == "error":
                self.logger.warning(f"Failed to log case {case_id}")

            notification_response = self.mcp_provider.call_tool(
                "notification_system", "send_notification",
                case_id=case_id,
                decision=decision.get("classification", "UNKNOWN"),
                applicant_email=applicant_email,
            )

            if notification_response["status"] == "error":
                self.logger.warning(f"Failed to send notification for {case_id}")

            execution_time_ms = (time.time() - start_time) * 1000

            action_summary = {
                "case_id": case_id,
                "action_taken": "NOTIFICATION_SENT_AND_LOGGED",
                "notification_sent": notification_response["status"] == "success",
                "case_logged": log_response["status"] == "success",
                "recipient": applicant_email,
                "timestamp": decision.get("timestamp", ""),
                "decision_summary": {
                    "classification": decision.get("classification"),
                    "risk_score": decision.get("risk_score"),
                    "confidence": decision.get("confidence_level"),
                },
            }

            self.logger.info(
                f"Compliance actions completed for case {case_id}: "
                f"Notification={'sent' if action_summary['notification_sent'] else 'failed'}, "
                f"Logged={'yes' if action_summary['case_logged'] else 'no'}"
            )

            return {
                "status": "success",
                "agent_name": self.name,
                "output": action_summary,
                "execution_time_ms": execution_time_ms,
            }

        except Exception as e:
            self.logger.error(f"Error in compliance orchestration: {str(e)}")
            return {
                "status": "error",
                "agent_name": self.name,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000,
            }
