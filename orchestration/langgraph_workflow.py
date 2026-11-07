from typing import Dict, Any, Annotated, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.models import LoanApplication, DecisionClassification
from shared.utils import get_logger, generate_case_id
from agents.applicant_profile_agent import ApplicantProfileAgent
from agents.financial_risk_agent import FinancialRiskAgent
from agents.loan_decision_agent import LoanDecisionAgent
from agents.compliance_orchestrator_agent import ComplianceOrchestratorAgent
from datetime import datetime
from langgraph.graph import StateGraph, END
import asyncio

logger = get_logger("LangGraphWorkflow")


class LoanApprovalGraphState(Dict):
    application: LoanApplication
    profile_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    final_decision: Dict[str, Any]
    compliance_action: Dict[str, Any]
    errors: List[str]
    execution_trace: List[Dict[str, Any]]


class LoanApprovalGraphWorkflow:
    def __init__(self):
        self.logger = get_logger("LoanApprovalGraphWorkflow")
        self.profile_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceOrchestratorAgent()
        self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(dict)

        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("run_profile_agent", self._run_profile_agent)
        workflow.add_node("run_risk_agent", self._run_risk_agent)
        workflow.add_node("run_decision_agent", self._run_decision_agent)
        workflow.add_node("run_compliance_agent", self._run_compliance_agent)
        workflow.add_node("format_response", self._format_response)

        workflow.set_entry_point("validate_input")

        workflow.add_edge("validate_input", "run_profile_agent")
        workflow.add_edge("run_profile_agent", "run_risk_agent")
        workflow.add_edge("run_risk_agent", "run_decision_agent")
        workflow.add_edge("run_decision_agent", "run_compliance_agent")
        workflow.add_edge("run_compliance_agent", "format_response")
        workflow.add_edge("format_response", END)

        self.graph = workflow.compile()

    def run(self, application: LoanApplication) -> Dict[str, Any]:
        self.logger.info(f"Starting LangGraph workflow for {application.applicant_id}")

        initial_state = {
            "application": application,
            "profile_analysis": None,
            "risk_analysis": None,
            "final_decision": None,
            "compliance_action": None,
            "errors": [],
            "execution_trace": [],
        }

        try:
            final_state = self.graph.invoke(initial_state)
            return final_state.get("formatted_response", final_state)
        except Exception as e:
            self.logger.error(f"Workflow error: {str(e)}")
            return {
                "status": "error",
                "classification": "REQUIRES_MANUAL_REVIEW",
                "risk_score": 75,
                "confidence_level": 0.0,
                "decision_factors": ["System error occurred during processing"],
                "explanation": f"Workflow error: {str(e)}",
                "case_id": generate_case_id(),
                "timestamp": datetime.utcnow().isoformat(),
                "errors": [str(e)],
            }

    def _validate_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Validating input")
        self._log_trace(state, "validate_input", "started", {})

        application = state.get("application")

        try:
            errors = []
            if not application.applicant_id:
                errors.append("Missing applicant_id")
            if application.credit_score < 300 or application.credit_score > 850:
                errors.append("Invalid credit score")
            if application.loan_amount <= 0:
                errors.append("Loan amount must be positive")

            if errors:
                state["errors"] = errors
                self._log_trace(state, "validate_input", "failed", {"errors": errors})
            else:
                self._log_trace(
                    state,
                    "validate_input",
                    "passed",
                    {"application_id": application.applicant_id},
                )
        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
            self._log_trace(state, "validate_input", "error", {"error": str(e)})

        return state

    def _run_profile_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running profile agent (parallel start)")
        self._log_trace(state, "run_profile_agent", "started", {})

        try:
            result = self.profile_agent.analyze(state["application"])
            if result["status"] == "success":
                state["profile_analysis"] = result["output"]
                self._log_trace(
                    state,
                    "run_profile_agent",
                    "completed",
                    {
                        "income_stability": result["output"].get("income_stability_score"),
                        "employment_risk": result["output"].get("employment_risk"),
                    },
                )
            else:
                state["errors"].append(f"Profile agent error: {result.get('error')}")
                self._log_trace(
                    state, "run_profile_agent", "failed", {"error": result.get("error")}
                )
        except Exception as e:
            state["errors"].append(f"Profile agent exception: {str(e)}")
            self._log_trace(state, "run_profile_agent", "error", {"error": str(e)})

        return state

    def _run_risk_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running risk agent (parallel with profile)")
        self._log_trace(state, "run_risk_agent", "started", {})

        try:
            result = self.risk_agent.analyze(state["application"])
            if result["status"] == "success":
                state["risk_analysis"] = result["output"]
                self._log_trace(
                    state,
                    "run_risk_agent",
                    "completed",
                    {
                        "dti_ratio": result["output"].get("debt_to_income_ratio"),
                        "credit_risk": result["output"].get("credit_score_risk_level"),
                        "anomalies": result["output"].get("anomaly_count", 0),
                    },
                )
            else:
                state["errors"].append(f"Risk agent error: {result.get('error')}")
                self._log_trace(
                    state, "run_risk_agent", "failed", {"error": result.get("error")}
                )
        except Exception as e:
            state["errors"].append(f"Risk agent exception: {str(e)}")
            self._log_trace(state, "run_risk_agent", "error", {"error": str(e)})

        return state

    def _run_decision_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running decision agent")
        self._log_trace(state, "run_decision_agent", "started", {})

        try:
            if state.get("errors"):
                state["final_decision"] = {
                    "classification": "REQUIRES_MANUAL_REVIEW",
                    "risk_score": 75,
                    "confidence_level": 0.0,
                    "decision_factors": ["Error in upstream agents"],
                    "explanation": "Unable to make decision due to upstream errors",
                    "case_id": generate_case_id(),
                }
                self._log_trace(
                    state,
                    "run_decision_agent",
                    "skipped",
                    {"reason": "upstream_errors"},
                )
                return state

            case_id = generate_case_id()
            result = self.decision_agent.decide(
                state.get("profile_analysis", {}),
                state.get("risk_analysis", {}),
                case_id,
            )

            if result["status"] == "success":
                state["final_decision"] = result["output"]
                self._log_trace(
                    state,
                    "run_decision_agent",
                    "completed",
                    {
                        "classification": result["output"].get("classification"),
                        "risk_score": result["output"].get("risk_score"),
                        "confidence": result["output"].get("confidence_level"),
                    },
                )
            else:
                state["errors"].append(f"Decision agent error: {result.get('error')}")
                self._log_trace(
                    state,
                    "run_decision_agent",
                    "failed",
                    {"error": result.get("error")},
                )
        except Exception as e:
            state["errors"].append(f"Decision agent exception: {str(e)}")
            self._log_trace(state, "run_decision_agent", "error", {"error": str(e)})

        return state

    def _run_compliance_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running compliance agent")
        self._log_trace(state, "run_compliance_agent", "started", {})

        try:
            decision = state.get("final_decision", {})
            result = self.compliance_agent.execute(
                decision,
                state["application"].applicant_id,
                applicant_email=f"{state['application'].applicant_id}@example.com",
            )

            if result["status"] == "success":
                state["compliance_action"] = result["output"]
                self._log_trace(
                    state,
                    "run_compliance_agent",
                    "completed",
                    {
                        "case_id": result["output"].get("case_id"),
                        "action": result["output"].get("action_taken"),
                    },
                )
            else:
                self.logger.warning(f"Compliance agent warning: {result.get('error')}")
                self._log_trace(
                    state,
                    "run_compliance_agent",
                    "warning",
                    {"error": result.get("error")},
                )
        except Exception as e:
            self.logger.warning(f"Compliance agent exception: {str(e)}")
            self._log_trace(state, "run_compliance_agent", "error", {"error": str(e)})

        return state

    def _format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Formatting response")

        if state.get("errors"):
            response = {
                "status": "error",
                "classification": "REQUIRES_MANUAL_REVIEW",
                "risk_score": 75,
                "confidence_level": 0.0,
                "decision_factors": ["System error occurred"],
                "explanation": "Unable to process application due to errors",
                "errors": state["errors"],
                "execution_trace": state.get("execution_trace", []),
                "case_id": generate_case_id(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            decision = state.get("final_decision", {})
            compliance = state.get("compliance_action", {})

            response = {
                "status": "success",
                "classification": decision.get("classification"),
                "risk_score": decision.get("risk_score"),
                "confidence_level": decision.get("confidence_level"),
                "decision_factors": decision.get("decision_factors", []),
                "explanation": decision.get("explanation"),
                "llm_explanation": decision.get("llm_explanation"),
                "case_id": compliance.get("case_id", generate_case_id()),
                "timestamp": decision.get("timestamp"),
                "execution_trace": state.get("execution_trace", []),
                "compliance_action": compliance.get("action_taken"),
            }

        state["formatted_response"] = response
        return state

    def _log_trace(
        self, state: Dict[str, Any], node: str, status: str, details: Dict[str, Any]
    ) -> None:
        entry = {
            "node": node,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        }
        if "execution_trace" not in state:
            state["execution_trace"] = []
        state["execution_trace"].append(entry)
