from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import get_logger
from mcp_servers.mcp_provider import MCPServerProvider
from shared.models import DecisionOutcome
import time
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

class LoanDecisionAgent:
    def __init__(self):
        self.name = "LoanDecisionAgent"
        self.logger = get_logger(self.name)
        self.mcp_provider = MCPServerProvider.get_instance()
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url=os.getenv("ANTHROPIC_BASE_URL")
        )

    def decide(
        self,
        profile_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        case_id: str,
    ) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Making loan decision for case {case_id}")

        try:
            synthesis_response = self.mcp_provider.call_tool(
                "decision_synthesis", "synthesize_decision",
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

            llm_explanation = self._get_llm_decision_explanation(
                decision_data, profile_analysis, risk_analysis
            )

            decision_outcome = DecisionOutcome(
                classification=decision_data["classification"],
                risk_score=decision_data["risk_score"],
                confidence_level=decision_data["confidence_level"],
                decision_factors=decision_data["decision_factors"],
                explanation=decision_data["explanation"],
                llm_explanation=llm_explanation,
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

    def _get_llm_decision_explanation(
        self,
        decision_data: Dict[str, Any],
        profile_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
    ) -> str:
        try:
            prompt = f"""You are a senior loan officer. Based on this analysis, provide a detailed decision explanation:

Classification: {decision_data['classification']}
Risk Score: {decision_data['risk_score']:.1f}/100
Confidence Level: {decision_data['confidence_level']:.2f}
Decision Factors: {', '.join(decision_data['decision_factors'])}

Income Stability: {profile_analysis.get('income_stability_score', 0)}/100
Employment Risk: {profile_analysis.get('employment_risk', 'unknown')}
DTI Ratio: {risk_analysis.get('debt_to_income_ratio', 0):.2f}
Credit Risk Level: {risk_analysis.get('credit_score_risk_level', 'unknown')}
Anomalies Detected: {len(risk_analysis.get('anomalies_detected', []))}

Provide a professional 3-4 sentence explanation justifying this decision for the applicant."""

            message = self.client.messages.create(
                model=os.getenv("ANTHROPIC_BASE_MODEL", "global.anthropic.claude-haiku-4-5-20251001-v1:0"),
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            self.logger.warning(f"LLM explanation failed: {str(e)}")
            return decision_data.get("explanation", "Decision based on risk assessment")
