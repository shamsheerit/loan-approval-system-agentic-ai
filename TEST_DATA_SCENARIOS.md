# Test Data - Three Decision Scenarios

This document provides test data for three distinct loan approval outcomes.

---

## Scenario 1: APPROVED

**Use these values in the Streamlit form:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_APPROVED_001` |
| Age | 40 |
| Annual Income | $85,000 |
| Employment Type | salaried |
| Credit Score | 780 |
| Loan Amount | $75,000 |
| Loan Tenure (Months) | 60 |
| Existing Liabilities | $5,000 |
| Location | New York |

**Expected Result:**
- ✅ Classification: **APPROVED**
- Risk Score: 15-25/100 (Low Risk)
- Confidence: 75-85%
- Decision Factors: Strong income stability, Favorable debt-to-income ratio, Good credit profile
- Explanation: Application approved based on strong financial profile

**Why This Gets Approved:**
- High credit score (780) = excellent credit profile
- Good income ($85k)
- Low DTI ratio (existing liabilities only $5k)
- Stable employment (salaried)
- Loan amount reasonable relative to income

---

## Scenario 2: REJECTED

**Use these values in the Streamlit form:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_REJECTED_001` |
| Age | 26 |
| Annual Income | $22,000 |
| Employment Type | self_employed |
| Credit Score | 480 |
| Loan Amount | $180,000 |
| Loan Tenure (Months) | 36 |
| Existing Liabilities | $45,000 |
| Location | Los Angeles |

**Expected Result:**
- ❌ Classification: **REJECTED**
- Risk Score: 75-85/100 (High Risk)
- Confidence: 60-75%
- Decision Factors: Weak income stability, High debt-to-income ratio, Poor credit profile, High loan-to-income ratio
- Explanation: Application rejected due to high financial risk

**Why This Gets Rejected:**
- Low credit score (480) = very poor credit
- Low income ($22k) vs high loan amount ($180k)
- Very high DTI ratio (liabilities $45k on $22k income)
- Self-employed (less stable income)
- Loan-to-income ratio extremely high (8.18x)
- Young age with risky profile

---

## Scenario 3: MANUAL REVIEW

**Use these values in the Streamlit form:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_REVIEW_001` |
| Age | 35 |
| Annual Income | $55,000 |
| Employment Type | business |
| Credit Score | 650 |
| Loan Amount | $120,000 |
| Loan Tenure (Months) | 60 |
| Existing Liabilities | $22,000 |
| Location | Chicago |

**Expected Result:**
- ⚠️ Classification: **REQUIRES_MANUAL_REVIEW**
- Risk Score: 40-60/100 (Moderate Risk)
- Confidence: 40-50%
- Decision Factors: Weak income stability, Moderate debt-to-income ratio, Fair credit profile, Multiple risk anomalies
- Explanation: Application requires manual review due to borderline risk metrics

**Why This Requires Review:**
- Fair credit score (650) = borderline credit
- Moderate DTI ratio (liabilities $22k on $55k income = 40%)
- Business owner = income variability
- Loan amount is 2.18x annual income (moderate risk)
- Profile has mixed signals requiring human judgment

---

## How to Test

### 1. Start the Backend
```bash
cd /home/ubuntu/loan-approval-system
python backend/main.py
```

### 2. Start Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

### 3. Test Each Scenario
- Open browser to http://localhost:8501
- Fill in form with values from each scenario
- Click "Submit Application"
- Observe the result

### 4. Verify Results
Compare actual results with expected results above

---

## Additional Test Cases (Optional)

### Edge Case 1: Young with Good Credit
```
Age: 23
Income: $45,000
Credit Score: 750
Loan Amount: $50,000
Liabilities: $2,000
Expected: APPROVED
```

### Edge Case 2: High Income, High Debt
```
Age: 45
Income: $150,000
Credit Score: 700
Loan Amount: $200,000
Liabilities: $80,000
DTI: 0.45 (still acceptable)
Expected: APPROVED or MANUAL_REVIEW
```

### Edge Case 3: Perfect Profile
```
Age: 38
Income: $120,000
Credit Score: 820
Loan Amount: $80,000
Liabilities: $3,000
DTI: 0.025 (excellent)
Expected: APPROVED (best case)
```

### Edge Case 4: Worst Profile
```
Age: 25
Income: $18,000
Credit Score: 350
Loan Amount: $250,000
Liabilities: $60,000
Expected: REJECTED (worst case)
```

---

## Decision Logic Summary

### APPROVED (Risk Score < 40)
- Good credit score (650+)
- DTI ratio < 0.43
- Income stability strong
- Loan-to-income reasonable
- No serious anomalies

### MANUAL_REVIEW (Risk Score 40-65)
- Fair/mixed credit profile
- DTI ratio 0.30-0.43
- Some anomalies detected
- Borderline income stability
- Requires human judgment

### REJECTED (Risk Score > 70)
- Poor credit score (< 600)
- High DTI ratio (> 0.43)
- High loan-to-income (> 3x)
- Multiple anomalies
- Weak income stability

---

## Notes

1. **Haiku Model**: Your configuration uses Claude Haiku for faster/cheaper processing
2. **Graceful Fallback**: If LLM calls fail, system uses rule-based explanations
3. **Execution Trace**: Expand "🔍 Execution Trace" to see all processing steps
4. **Decision Factors**: Shows which metrics influenced the decision
5. **Case ID**: Unique identifier for audit trail and case tracking

---

*Last Updated: 2026-11-07*
