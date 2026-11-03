from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class EmploymentTypeRequest(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS = "business"

class ApplicantProfileRequest(BaseModel):
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    employment_type: EmploymentTypeRequest

class LoanApplicationRequest(BaseModel):
    applicant_id: str
    applicant_profile: ApplicantProfileRequest
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    existing_liabilities: float = Field(..., ge=0)
    location: str

class LoanDecisionResponse(BaseModel):
    status: str
    classification: str
    risk_score: float
    confidence_level: float
    decision_factors: List[str]
    explanation: str
    case_id: str
    timestamp: str
    execution_trace: Optional[List[dict]] = None
    errors: Optional[List[str]] = None

class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: str
    decision: Optional[LoanDecisionResponse] = None

class HealthCheckResponse(BaseModel):
    status: str
    message: str
