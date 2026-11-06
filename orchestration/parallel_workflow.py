from typing import Dict, Any, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.models import LoanApplication
from shared.utils import get_logger, generate_case_id
from agents.applicant_profile_agent import ApplicantProfileAgent
from agents.financial_risk_agent import FinancialRiskAgent
from agents.loan_decision_agent import LoanDecisionAgent
from agents.compliance_orchestrator_agent import ComplianceOrchestratorAgent
from datetime import datetime
import asyncio

logger = get_logger("ParallelWorkflow")


class ParallelLoanApprovalWorkflow:
    def __init__(self):
        self.logger = get_logger("ParallelLoanApprovalWorkflow")
        self.profile_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceOrchestratorAgent()

    def run(self, application: LoanApplication) -> Dict[str, Any]:
        self.logger.info(
            f"Starting parallel workflow for {application.applicant_id}"
        )
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

        state = self._run_parallel_agents(state)

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
                self._log_trace(
                    "validate_input", "passed", {"application_id": application.applicant_id}
                )

        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
            state["has_errors"] = True
            self._log_trace("validate_input", "error", {"error": str(e)})

        return state

    def _run_parallel_agents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run profile and risk agents in parallel using asyncio"""
        self.logger.info("Running profile and risk agents in parallel")
        self._log_trace("run_parallel_agents", "started", {})

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            profile_result, risk_result = loop.run_until_complete(
                self._execute_parallel(state["application"])
            )
            loop.close()

            if profile_result["status"] == "success":
                state["profile_analysis"] = profile_result["output"]
                self._log_trace(
                    "run_profile_agent",
                    "completed",
                    {
                        "income_stability_score": profile_result["output"].get(
                            "income_stability_score"
                        ),
                        "employment_risk": profile_result["output"].get("employment_risk"),
                    },
                )
            else:
                state["errors"].append(f"Profile agent error: {profile_result.get('error')}")
                state["has_errors"] = True
                self._log_trace(
                    "run_profile_agent", "failed", {"error": profile_result.get("error")}
                )

            if risk_result["status"] == "success":
                state["risk_analysis"] = risk_result["output"]
                self._log_trace(
                    "run_risk_agent",
                    "completed",
                    {
                        "dti_ratio": risk_result["output"].get("debt_to_income_ratio"),
                        "credit_risk_level": risk_result["output"].get(
                            "credit_score_risk_level"
                        ),
                        "anomaly_count": risk_result["output"].get("anomaly_count", 0),
                    },
                )
            else:
                state["errors"].append(f"Risk agent error: {risk_result.get('error')}")
                state["has_errors"] = True
                self._log_trace(
                    "run_risk_agent", "failed", {"error": risk_result.get("error")}
                )

            self._log_trace(
                "run_parallel_agents",
                "completed",
                {
                    "profile_status": profile_result["status"],
                    "risk_status": risk_result["status"],
                },
            )

        except Exception as e:
            state["errors"].append(f"Parallel execution error: {str(e)}")
            state["has_errors"] = True
            self._log_trace("run_parallel_agents", "error", {"error": str(e)})

        return state

    async def _execute_parallel(self, application: LoanApplication) -> tuple:
        """Execute profile and risk agents concurrently"""
        profile_task = asyncio.to_thread(self.profile_agent.analyze, application)
        risk_task = asyncio.to_thread(self.risk_agent.analyze, application)

        results = await asyncio.gather(profile_task, risk_task)
        return results[0], results[1]

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
                self._log_trace(
                    "run_decision_agent", "failed", {"error": result.get("error")}
                )

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
                self._log_trace(
                    "run_compliance_agent", "warning", {"error": result.get("error")}
                )

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
