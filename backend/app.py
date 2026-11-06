from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, Any
from shared.models import LoanApplication, EmploymentType, ApplicantProfile
from shared.utils import get_logger, generate_application_id
from orchestration.parallel_workflow import ParallelLoanApprovalWorkflow
from .schemas import (
    LoanApplicationRequest,
    LoanDecisionResponse,
    ApplicationStatusResponse,
    HealthCheckResponse,
)
from datetime import datetime

app = FastAPI(
    title="Loan Approval System API",
    description="Multi-Agent Agentic AI Loan Approval System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("FastAPI")

applications_cache: Dict[str, Dict[str, Any]] = {}
workflow = ParallelLoanApprovalWorkflow()

@app.post("/api/loan/submit", response_model=ApplicationStatusResponse)
async def submit_loan_application(request: LoanApplicationRequest):
    """Submit a loan application for processing"""
    logger.info(f"Received loan application for {request.applicant_id}")

    try:
        application_id = generate_application_id()

        employment_type_map = {
            "salaried": EmploymentType.SALARIED,
            "self_employed": EmploymentType.SELF_EMPLOYED,
            "business": EmploymentType.BUSINESS,
        }

        employment_type = employment_type_map.get(
            request.applicant_profile.employment_type, EmploymentType.SALARIED
        )

        applicant_profile = ApplicantProfile(
            age=request.applicant_profile.age,
            income=request.applicant_profile.income,
            employment_type=employment_type,
        )

        application = LoanApplication(
            applicant_id=request.applicant_id,
            applicant_profile=applicant_profile,
            credit_score=request.credit_score,
            loan_amount=request.loan_amount,
            tenure_months=request.tenure_months,
            existing_liabilities=request.existing_liabilities,
            location=request.location,
        )

        applications_cache[application_id] = {
            "application": application,
            "status": "processing",
            "submitted_at": datetime.utcnow().isoformat(),
        }

        loop = asyncio.get_event_loop()
        loop.create_task(
            process_application_async(application_id, application)
        )

        return ApplicationStatusResponse(
            application_id=application_id,
            status="submitted",
            decision=None,
        )

    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/loan/status/{application_id}", response_model=ApplicationStatusResponse)
async def check_application_status(application_id: str):
    """Check the status of a loan application"""
    logger.info(f"Checking status for {application_id}")

    if application_id not in applications_cache:
        raise HTTPException(status_code=404, detail="Application not found")

    cached = applications_cache[application_id]
    status = cached["status"]

    if status == "completed":
        decision = cached["decision"]
        return ApplicationStatusResponse(
            application_id=application_id,
            status="completed",
            decision=LoanDecisionResponse(
                status="success",
                classification=decision.get("classification"),
                risk_score=decision.get("risk_score"),
                confidence_level=decision.get("confidence_level"),
                decision_factors=decision.get("decision_factors", []),
                explanation=decision.get("explanation"),
                case_id=decision.get("case_id"),
                timestamp=decision.get("timestamp"),
                execution_trace=decision.get("execution_trace"),
            ),
        )
    else:
        return ApplicationStatusResponse(
            application_id=application_id,
            status=status,
            decision=None,
        )

@app.get("/api/loan/decision/{application_id}", response_model=LoanDecisionResponse)
async def get_loan_decision(application_id: str):
    """Get the final loan decision"""
    logger.info(f"Retrieving decision for {application_id}")

    if application_id not in applications_cache:
        raise HTTPException(status_code=404, detail="Application not found")

    cached = applications_cache[application_id]

    if cached["status"] != "completed":
        raise HTTPException(
            status_code=202, detail="Decision not yet available - still processing"
        )

    decision = cached["decision"]
    return LoanDecisionResponse(
        status="success",
        classification=decision.get("classification"),
        risk_score=decision.get("risk_score"),
        confidence_level=decision.get("confidence_level"),
        decision_factors=decision.get("decision_factors", []),
        explanation=decision.get("explanation"),
        case_id=decision.get("case_id"),
        timestamp=decision.get("timestamp"),
        execution_trace=decision.get("execution_trace"),
        errors=decision.get("errors"),
    )

@app.post("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        message="Loan Approval System is operational",
    )

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check_get():
    """Health check endpoint (GET)"""
    return HealthCheckResponse(
        status="healthy",
        message="Loan Approval System is operational",
    )

async def process_application_async(application_id: str, application: LoanApplication):
    """Process loan application asynchronously"""
    try:
        logger.info(f"Processing application {application_id}")

        decision = workflow.run(application)

        # Convert datetime to ISO format string
        if isinstance(decision.get("timestamp"), object) and hasattr(decision.get("timestamp"), "isoformat"):
            decision["timestamp"] = decision["timestamp"].isoformat()

        applications_cache[application_id]["decision"] = decision
        applications_cache[application_id]["status"] = "completed"

        logger.info(
            f"Application {application_id} processed: {decision.get('classification')}"
        )

    except Exception as e:
        logger.error(f"Error processing application {application_id}: {str(e)}")
        applications_cache[application_id]["status"] = "error"
        applications_cache[application_id]["decision"] = {
            "classification": "REQUIRES_MANUAL_REVIEW",
            "risk_score": 0,
            "confidence_level": 0,
            "decision_factors": ["Processing error"],
            "explanation": f"Error: {str(e)}",
            "case_id": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "errors": [str(e)],
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
