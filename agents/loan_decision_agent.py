from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger
from mcp_servers.decision_synthesis import DecisionSynthesisServer
from shared.models import DecisionOutcome
import time

class LoanDecisionAgent:
    def __init__(self):
        self.name = "LoanDecisionAgent"
        self.logger = get_logger(self.name)
        self.mcp_server = DecisionSynthesisServer()

    def decide(
        self,
        profile_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        case_id: str,
    ) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Making loan decision for case {case_id}")

        try:
            synthesis_response = self.mcp_server.call_tool(
                "synthesize_decision",
                profile_analysis=profile_analysis,
                risk_analysis=risk_analysis,
            )

            if synthesis_response["status"] == "error":
                return {
                    "status": "error",
                    "agent_name": self.name,
                    "error": synthesis_response.get("error", "Synthesis failed"),
                }

            decision_data = synthesis_response["result"]

            decision_outcome = DecisionOutcome(
                classification=decision_data["classification"],
                risk_score=decision_data["risk_score"],
                confidence_level=decision_data["confidence_level"],
                decision_factors=decision_data["decision_factors"],
                explanation=decision_data["explanation"],
                case_id=case_id,
            )

            execution_time_ms = (time.time() - start_time) * 1000

            self.logger.info(
                f"Decision for {case_id}: {decision_outcome.classification} "
                f"(Risk: {decision_outcome.risk_score}, Confidence: {decision_outcome.confidence_level})"
            )

            return {
                "status": "success",
                "agent_name": self.name,
                "output": decision_outcome.model_dump(),
                "execution_time_ms": execution_time_ms,
            }

        except Exception as e:
            self.logger.error(f"Error in loan decision: {str(e)}")
            return {
                "status": "error",
                "agent_name": self.name,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000,
            }
