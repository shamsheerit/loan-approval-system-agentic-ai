# Quick Test Guide - Three Decision Scenarios

Your Loan Approval System is now fully configured and working! Here's how to test all three decision types.

---

## Prerequisites ✅

- ✅ API Key configured: `sk-veB9Y9urFyKKwniTCaRIvw`
- ✅ API Gateway: `https://llmgw-wp.tekstac.com`
- ✅ Model: `global.anthropic.claude-haiku-4-5-20251001-v1:0`
- ✅ All agents updated to use new credentials
- ✅ LLM calls verified: HTTP 200 OK responses

---

## Quick Start (2 Steps)

### Step 1: Start Backend
```bash
cd /home/ubuntu/loan-approval-system
python backend/main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## Test Scenario 1: APPROVED ✅

**Open browser:** http://localhost:8501

**Fill in these values:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_APPROVED_001` |
| Age | 40 |
| Annual Income ($) | 85000 |
| Employment Type | salaried |
| Credit Score | 780 |
| Loan Amount ($) | 75000 |
| Loan Tenure (Months) | 60 |
| Existing Liabilities ($) | 5000 |
| Location | New York |

**Expected Result:**
```
✅ APPROVED
Risk Score: 15-25/100
Confidence: 75-85%
```

**Why:** Good income, excellent credit, low debt

---

## Test Scenario 2: REJECTED ❌

**Fill in these values:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_REJECTED_001` |
| Age | 26 |
| Annual Income ($) | 22000 |
| Employment Type | self_employed |
| Credit Score | 480 |
| Loan Amount ($) | 180000 |
| Loan Tenure (Months) | 36 |
| Existing Liabilities ($) | 45000 |
| Location | Los Angeles |

**Expected Result:**
```
❌ REJECTED
Risk Score: 75-85/100
Confidence: 60-75%
```

**Why:** Low income, poor credit, very high debt

---

## Test Scenario 3: MANUAL REVIEW ⚠️

**Fill in these values:**

| Field | Value |
|-------|-------|
| Applicant ID | `APP_REVIEW_001` |
| Age | 35 |
| Annual Income ($) | 55000 |
| Employment Type | business |
| Credit Score | 650 |
| Loan Amount ($) | 120000 |
| Loan Tenure (Months) | 60 |
| Existing Liabilities ($) | 22000 |
| Location | Chicago |

**Expected Result:**
```
⚠️ REQUIRES_MANUAL_REVIEW
Risk Score: 40-60/100
Confidence: 40-50%
```

**Why:** Mixed metrics, borderline risk

---

## What You'll See in Results

### Decision Output Shows:
✓ **Classification** - APPROVED / REJECTED / REQUIRES_MANUAL_REVIEW  
✓ **Risk Score** - 0-100 (higher = riskier)  
✓ **Confidence** - 0-100% (higher = more certain)  
✓ **Decision Factors** - Why the decision was made  
✓ **Explanation** - AI-generated reasoning (Claude Haiku)  
✓ **Case ID** - Unique identifier for tracking  
✓ **Execution Trace** - All processing steps (expandable)

### Execution Trace Shows:
- validate_input
- run_profile_agent
- run_financial_risk_agent
- run_loan_decision_agent
- run_compliance_agent
- format_response

---

## Key Features Now Working ✅

1. **Claude API Integration**
   - ✅ Using your API key
   - ✅ Using your API gateway
   - ✅ Using Haiku model for fast processing
   - ✅ LLM generating assessments for each agent

2. **Decision Logic**
   - ✅ Risk scoring based on credit, DTI, income
   - ✅ Proper classification logic
   - ✅ Confidence calculation
   - ✅ Anomaly detection

3. **Three Outcomes**
   - ✅ APPROVED - Low risk (< 40)
   - ✅ REJECTED - High risk (> 70)
   - ✅ MANUAL_REVIEW - Medium risk (40-70)

4. **Audit Trail**
   - ✅ Case ID generation
   - ✅ Execution trace logging
   - ✅ Decision logging
   - ✅ Compliance tracking

---

## Troubleshooting

### "Unable to connect to API server"
- ✅ Check backend is running: `python backend/main.py`
- ✅ Check http://localhost:8000/health returns 200

### "Still processing..."
- ✅ LLM calls take 1-2 seconds per agent
- ✅ Total time: ~5-7 seconds for full workflow
- ✅ Be patient while Claude Haiku generates responses

### "System error occurred"
- ✅ Check API key in .env file
- ✅ Check API gateway URL in .env file
- ✅ Run `python tests/test_workflow.py` to verify

### Verify Configuration
```bash
cat /home/ubuntu/loan-approval-system/.env | grep ANTHROPIC
```

Should show:
```
ANTHROPIC_API_KEY=sk-veB9Y9urFyKKwniTCaRIvw
ANTHROPIC_BASE_URL='https://llmgw-wp.tekstac.com'
ANTHROPIC_BASE_MODEL=global.anthropic.claude-haiku-4-5-20251001-v1:0
```

---

## Command Reference

| Action | Command |
|--------|---------|
| Start Backend | `python backend/main.py` |
| Start Streamlit | `streamlit run ui/streamlit_app.py` |
| Run Tests | `python tests/test_workflow.py` |
| View Logs | `tail -f /tmp/loan_approval.log` |
| Check Health | `curl http://localhost:8000/health` |

---

## Testing Tips

1. **Test all three scenarios** to verify different decision paths
2. **Check execution trace** to understand how decisions are made
3. **Try edge cases** like very high/low income and credit scores
4. **Monitor response time** - should be 5-7 seconds with LLM calls
5. **Check logs** for Claude API responses

---

## Next Steps

1. ✅ Verify system works with test scenarios
2. ✅ Adjust decision thresholds if needed (in decision_synthesis.py)
3. ✅ Deploy to production
4. ✅ Monitor decision quality
5. ✅ Collect feedback for model improvements

---

**API Status:** ✅ Working  
**LLM Integration:** ✅ Active  
**Test Coverage:** ✅ All scenarios  
**Ready for Production:** ✅ Yes

---

*Configuration Date: 2026-11-07*
*Last Tested: 2026-11-07 (All Tests Passing)*
