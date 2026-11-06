from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any

class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS = "business"

class DecisionClassification(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "REQUIRES_MANUAL_REVIEW"

class ApplicantProfile(BaseModel):
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    employment_type: EmploymentType

class LoanApplication(BaseModel):
    applicant_id: str
    applicant_profile: ApplicantProfile
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    existing_liabilities: float = Field(..., ge=0)
    location: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ProfileAnalysis(BaseModel):
    income_stability_score: float = Field(..., ge=0, le=100)
    employment_risk: str
    credit_history_summary: str
    application_completeness_flags: List[str] = Field(default_factory=list)
    llm_assessment: Optional[str] = None

class RiskAnalysis(BaseModel):
    debt_to_income_ratio: float = Field(..., ge=0)
    credit_score_risk_level: str
    loan_amount_risk: str
    anomalies_detected: List[str] = Field(default_factory=list)
    reasoning: str
    llm_analysis: Optional[str] = None

class DecisionOutcome(BaseModel):
    classification: DecisionClassification
    risk_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=1)
    decision_factors: List[str]
    explanation: str
    llm_explanation: Optional[str] = None
    case_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    output: Dict[str, Any]
    execution_time_ms: float
    error: Optional[str] = None
