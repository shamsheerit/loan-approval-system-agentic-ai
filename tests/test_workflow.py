import sys
sys.path.insert(0, '/home/ubuntu/loan-approval-system')

from shared.models import (
    LoanApplication,
    ApplicantProfile,
    EmploymentType,
    DecisionClassification,
)
from orchestration.loan_approval_workflow import LoanApprovalWorkflow
from datetime import datetime

def test_workflow_approved_applicant():
    """Test workflow with an approved applicant"""
    workflow = LoanApprovalWorkflow()

    application = LoanApplication(
        applicant_id="APP001",
        applicant_profile=ApplicantProfile(
            age=35,
            income=60000,
            employment_type=EmploymentType.SALARIED,
        ),
        credit_score=750,
        loan_amount=100000,
        tenure_months=60,
        existing_liabilities=10000,
        location="New York",
    )

    result = workflow.run(application)

    assert result["status"] == "success"
    assert result["classification"] in ["APPROVED", "REJECTED", "REQUIRES_MANUAL_REVIEW"]
    assert 0 <= result["risk_score"] <= 100
    assert 0 <= result["confidence_level"] <= 1
    assert len(result["decision_factors"]) > 0
    assert result["case_id"].startswith("CASE-")
    print(f"✅ Test passed: {result['classification']}")

def test_workflow_rejected_applicant():
    """Test workflow with a rejected applicant"""
    workflow = LoanApprovalWorkflow()

    application = LoanApplication(
        applicant_id="APP002",
        applicant_profile=ApplicantProfile(
            age=28,
            income=25000,
            employment_type=EmploymentType.SELF_EMPLOYED,
        ),
        credit_score=550,
        loan_amount=200000,
        tenure_months=36,
        existing_liabilities=50000,
        location="Los Angeles",
    )

    result = workflow.run(application)

    assert result["status"] == "success"
    assert result["classification"] in ["APPROVED", "REJECTED", "REQUIRES_MANUAL_REVIEW"]
    print(f"✅ Test passed: {result['classification']}")

def test_workflow_edge_case():
    """Test workflow with edge case applicant"""
    workflow = LoanApprovalWorkflow()

    application = LoanApplication(
        applicant_id="APP003",
        applicant_profile=ApplicantProfile(
            age=22,
            income=35000,
            employment_type=EmploymentType.BUSINESS,
        ),
        credit_score=650,
        loan_amount=150000,
        tenure_months=48,
        existing_liabilities=30000,
        location="Chicago",
    )

    result = workflow.run(application)

    assert result["status"] == "success"
    print(f"✅ Test passed: {result['classification']}")

if __name__ == "__main__":
    print("Running workflow tests...\n")
    test_workflow_approved_applicant()
    test_workflow_rejected_applicant()
    test_workflow_edge_case()
    print("\n✅ All workflow tests passed!")
