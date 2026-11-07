from typing import Dict, Any, Annotated
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
import asyncio

logger = get_logger("LoanApprovalWorkflow")

class WorkflowState(Dict):
    pass

class LoanApprovalWorkflow:
    def __init__(self):
        self.logger = get_logger("LoanApprovalWorkflow")
        self.profile_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceOrchestratorAgent()
        self.execution_trace = []

    def run(self, application: LoanApplication) -> Dict[str, Any]:
        self.logger.info(f"Starting workflow for application {application.applicant_id}")
        self.execution_trace = []

        state = {
            "application": application,
            "profile_analysis": None,
            "risk_analysis": None,
            "final_decision": None,
            "errors": [],
            "execution_trace": [],
        }

        state = self._validate_input(state)
        if state.get("has_errors"):
            return self._format_response(state)

        state = self._run_profile_agent(state)
        state = self._run_risk_agent(state)

        if state.get("has_errors"):
            return self._format_response(state)

        state = self._run_decision_agent(state)

        if state.get("has_errors"):
            return self._format_response(state)

        state = self._run_compliance_agent(state)

        return self._format_response(state)

    def _validate_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Validating input application data")
        self._log_trace("validate_input", "started", {})

        try:
            application = state["application"]

            if not application.applicant_id:
                state["errors"].append("Missing applicant_id")

            if application.credit_score < 300 or application.credit_score > 850:
                state["errors"].append("Invalid credit score")

            if application.loan_amount <= 0:
                state["errors"].append("Loan amount must be positive")

            if len(state["errors"]) > 0:
                state["has_errors"] = True
                self._log_trace("validate_input", "failed", {"errors": state["errors"]})
            else:
                self._log_trace("validate_input", "passed", {"application_id": application.applicant_id})

        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
            state["has_errors"] = True
            self._log_trace("validate_input", "error", {"error": str(e)})

        return state

    def _run_profile_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running Applicant Profile Agent")
        self._log_trace("run_profile_agent", "started", {})

        try:
            result = self.profile_agent.analyze(state["application"])

            if result["status"] == "success":
                state["profile_analysis"] = result["output"]
                self._log_trace(
                    "run_profile_agent",
                    "completed",
                    {
                        "income_stability_score": result["output"].get("income_stability_score"),
                        "employment_risk": result["output"].get("employment_risk"),
                    },
                )
            else:
                state["errors"].append(f"Profile agent error: {result.get('error')}")
                state["has_errors"] = True
                self._log_trace("run_profile_agent", "failed", {"error": result.get("error")})

        except Exception as e:
            state["errors"].append(f"Profile agent exception: {str(e)}")
            state["has_errors"] = True
            self._log_trace("run_profile_agent", "error", {"error": str(e)})

        return state

    def _run_risk_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running Financial Risk Agent")
        self._log_trace("run_risk_agent", "started", {})

        try:
            result = self.risk_agent.analyze(state["application"])

            if result["status"] == "success":
                state["risk_analysis"] = result["output"]
                self._log_trace(
                    "run_risk_agent",
                    "completed",
                    {
                        "dti_ratio": result["output"].get("debt_to_income_ratio"),
                        "credit_risk_level": result["output"].get("credit_score_risk_level"),
                        "anomaly_count": result["output"].get("anomaly_count", 0),
                    },
                )
            else:
                state["errors"].append(f"Risk agent error: {result.get('error')}")
                state["has_errors"] = True
                self._log_trace("run_risk_agent", "failed", {"error": result.get("error")})

        except Exception as e:
            state["errors"].append(f"Risk agent exception: {str(e)}")
            state["has_errors"] = True
            self._log_trace("run_risk_agent", "error", {"error": str(e)})

        return state

    def _run_decision_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running Loan Decision Agent")
        self._log_trace("run_decision_agent", "started", {})

        try:
            case_id = generate_case_id()
            result = self.decision_agent.decide(
                state["profile_analysis"], state["risk_analysis"], case_id
            )

            if result["status"] == "success":
                state["final_decision"] = result["output"]
                self._log_trace(
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
                state["has_errors"] = True
                self._log_trace("run_decision_agent", "failed", {"error": result.get("error")})

        except Exception as e:
            state["errors"].append(f"Decision agent exception: {str(e)}")
            state["has_errors"] = True
            self._log_trace("run_decision_agent", "error", {"error": str(e)})

        return state

    def _run_compliance_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Running Compliance & Action Orchestrator Agent")
        self._log_trace("run_compliance_agent", "started", {})

        try:
            result = self.compliance_agent.execute(
                state["final_decision"],
                state["application"].applicant_id,
                applicant_email=f"{state['application'].applicant_id}@example.com",
            )

            if result["status"] == "success":
                state["compliance_action"] = result["output"]
                self._log_trace(
                    "run_compliance_agent",
                    "completed",
                    {
                        "case_id": result["output"].get("case_id"),
                        "action_taken": result["output"].get("action_taken"),
                    },
                )
            else:
                self.logger.warning(f"Compliance agent warning: {result.get('error')}")
                self._log_trace("run_compliance_agent", "warning", {"error": result.get("error")})

        except Exception as e:
            self.logger.warning(f"Compliance agent exception: {str(e)}")
            self._log_trace("run_compliance_agent", "error", {"error": str(e)})

        return state

    def _format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Formatting final response")

        if state.get("has_errors"):
            return {
                "status": "error",
                "classification": "REQUIRES_MANUAL_REVIEW",
                "risk_score": 75,
                "confidence_level": 0.0,
                "decision_factors": ["System error occurred during processing"],
                "explanation": "Unable to process application due to system errors. Please contact support.",
                "errors": state["errors"],
                "execution_trace": state.get("execution_trace", []),
                "case_id": generate_case_id(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        decision = state.get("final_decision", {})
        compliance_action = state.get("compliance_action", {})

        return {
            "status": "success",
            "classification": decision.get("classification"),
            "risk_score": decision.get("risk_score"),
            "confidence_level": decision.get("confidence_level"),
            "decision_factors": decision.get("decision_factors", []),
            "explanation": decision.get("explanation"),
            "llm_explanation": decision.get("llm_explanation"),
            "case_id": compliance_action.get("case_id", generate_case_id()),
            "timestamp": decision.get("timestamp"),
            "execution_trace": state.get("execution_trace", []),
            "compliance_action": compliance_action.get("action_taken"),
        }

    def _log_trace(self, node_name: str, status: str, details: Dict[str, Any]) -> None:
        trace_entry = {
            "node": node_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        }
        self.execution_trace.append(trace_entry)

        if not hasattr(self, "_current_state") or self._current_state is None:
            self._current_state = {}

        if "execution_trace" not in self._current_state:
            self._current_state["execution_trace"] = []

        self._current_state["execution_trace"].append(trace_entry)
