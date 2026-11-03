from .base_server import BaseMCPServer
from typing import Dict, Any
from datetime import datetime
from shared.utils import get_logger

class NotificationSystemServer(BaseMCPServer):
    def __init__(self):
        self.case_log = []
        self.logger = get_logger("NotificationSystemServer")
        super().__init__("NotificationSystemServer")

    def _register_tools(self):
        self.tools["send_notification"] = self.send_notification
        self.tools["log_case"] = self.log_case
        self.tools["get_case_history"] = self.get_case_history

    def send_notification(
        self, case_id: str, decision: str, applicant_email: str = "applicant@example.com"
    ) -> Dict[str, Any]:
        notification_data = {
            "case_id": case_id,
            "decision": decision,
            "recipient_email": applicant_email,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent",
        }

        self.logger.info(
            f"Notification sent for case {case_id}: {decision} to {applicant_email}"
        )

        return {
            "status": "success",
            "case_id": case_id,
            "notification_sent": True,
            "recipient": applicant_email,
            "message": f"Decision notification for {decision} sent to {applicant_email}",
        }

    def log_case(
        self,
        case_id: str,
        decision: str,
        risk_score: float,
        decision_factors: list,
        applicant_id: str = "unknown",
    ) -> Dict[str, Any]:
        case_entry = {
            "case_id": case_id,
            "applicant_id": applicant_id,
            "decision": decision,
            "risk_score": risk_score,
            "decision_factors": decision_factors,
            "logged_at": datetime.utcnow().isoformat(),
            "audit_status": "logged",
        }

        self.case_log.append(case_entry)
        self.logger.info(
            f"Case {case_id} logged with decision: {decision}, risk score: {risk_score}"
        )

        return {
            "status": "success",
            "case_id": case_id,
            "log_entry_created": True,
            "audit_timestamp": case_entry["logged_at"],
            "message": f"Case {case_id} successfully logged in audit trail",
        }

    def get_case_history(self, limit: int = 10) -> Dict[str, Any]:
        recent_cases = self.case_log[-limit:]

        return {
            "status": "success",
            "total_cases_logged": len(self.case_log),
            "recent_cases_count": len(recent_cases),
            "cases": recent_cases,
        }
