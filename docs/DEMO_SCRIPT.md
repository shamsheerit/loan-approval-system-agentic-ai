# Agentic AI Loan Approval System - Demo Script

## Demo Overview (15-20 minutes)

This guide walks through demonstrating the Multi-Agent Agentic AI Loan Approval System.

### Prerequisites
- FastAPI backend running: `python backend/main.py`
- Streamlit UI accessible: `streamlit run ui/streamlit_app.py`
- Anthropic API key configured in `.env`

---

## Demo Flow

### 1. System Overview (2 minutes)

**Talk through:**
- Multi-agent architecture with 4 specialized agents
- Each agent has a single, well-defined responsibility
- Agents communicate through standardized MCP (Model Context Protocol) servers
- LangGraph orchestrates the workflow with parallel agent execution
- Decision is fully explainable with audit trail

**Show:**
```
Presentation Layer (Streamlit UI)
           ↓
API Gateway (FastAPI)
           ↓
Orchestration (LangGraph Workflow)
           ↓
Agents (Profile, Risk, Decision, Compliance)
           ↓
MCP Servers (ApplicantDB, RiskRulesDB, DecisionSynthesis, NotificationSystem)
```

---

### 2. Demo Scenario A: Clear Approval (5 minutes)

**Use Test Data:**
- Applicant ID: `APP001`
- Age: 35
- Annual Income: $60,000
- Employment: Salaried
- Credit Score: 750
- Loan Amount: $100,000
- Tenure: 60 months
- Existing Liabilities: $10,000
- Location: New York

**Actions:**
1. Open Streamlit UI
2. Fill in the form with values above
3. Click "Submit Application"
4. Show the loading spinner

**Explain during processing:**
> "The system is now coordinating four agents in parallel:
> 1. The Applicant Profile Agent is analyzing employment history and income stability
> 2. The Financial Risk Agent is calculating DTI ratio and credit risk metrics
> 3. Once both complete, the Loan Decision Agent synthesizes the analysis
> 4. Finally, the Compliance Agent logs the decision and sends notifications"

**Show Results:**
- Green ✅ APPROVED badge
- Risk Score: Low (around 20-30)
- High confidence (80%+)
- Decision factors highlight strong income, good credit
- Execution trace shows all agents ran successfully

---

### 3. Demo Scenario B: Clear Rejection (5 minutes)

**Use Test Data:**
- Applicant ID: `APP002`
- Age: 28
- Annual Income: $25,000
- Employment: Self-Employed
- Credit Score: 550
- Loan Amount: $200,000
- Tenure: 36 months
- Existing Liabilities: $50,000
- Location: Los Angeles

**Talk Points:**
> "This application has multiple risk factors:
> - Low income compared to loan amount
> - Low credit score indicating previous financial difficulties
> - High existing liabilities
> - Loan-to-income ratio far exceeds safe thresholds"

**Show Results:**
- Red ❌ REJECTED badge
- Risk Score: High (70+)
- Low confidence
- Decision factors clearly explain rejection
- Highlights specific risk metrics

---

### 4. Demo Scenario C: Manual Review Required (5 minutes)

**Use Test Data:**
- Applicant ID: `APP003`
- Age: 45
- Annual Income: $120,000
- Employment: Business
- Credit Score: 680
- Loan Amount: $150,000
- Tenure: 48 months
- Existing Liabilities: $60,000
- Location: San Francisco

**Explain:**
> "This application is borderline. DTI ratio is on the edge of acceptable,
> and while income is solid, the self-employment adds complexity.
> The system routes this to manual review for a human expert."

**Show Results:**
- Orange ⚠️ REQUIRES_MANUAL_REVIEW badge
- Moderate risk score (40-60)
- Moderate confidence
- Multiple factors listed for reviewer

---

### 5. Live Code Modification (3 minutes)

**Show how architecture enables changes:**

1. Open `mcp-servers/risk_rules.py`
2. Show the credit score thresholds:
   ```python
   "excellent": (750, 850),
   "good": (700, 749),
   ```

3. Explain: "Suppose we want to be more inclusive and lower the 'good' threshold to 680"

4. Make a small adjustment:
   ```python
   "good": (680, 749),  # Changed from 700
   ```

5. Save and rerun the SAME application
6. Show how the risk score changes slightly due to credit risk recalibration
7. Highlight that this demonstrates:
   - Modular architecture
   - Easy configuration changes
   - Clear cause-and-effect

---

### 6. Explainability & Audit Trail (2 minutes)

**Expand "Execution Trace" section:**

Show the JSON structure:
```json
[
  {
    "node": "validate_input",
    "status": "passed",
    "timestamp": "2026-11-03T13:02:00.000Z",
    "details": {"application_id": "APP001"}
  },
  {
    "node": "run_profile_agent",
    "status": "completed",
    "details": {
      "income_stability_score": 85,
      "employment_risk": "low"
    }
  },
  ...
]
```

**Talk Points:**
> "Every decision is fully auditable. We can see exactly:
> - What each agent analyzed
> - What signals they identified
> - How the orchestration coordinated them
> - Final reasoning for the classification
> 
> This is critical for regulated industries like banking where
> decisions must be explainable and defensible."

---

## Key Messages to Convey

1. **Agentic AI Architecture**: Clear separation of concerns, each agent focused on one task
2. **Parallel Execution**: Profile and Risk agents run simultaneously for efficiency
3. **Explainability**: Full audit trail shows decision reasoning
4. **Modularity**: Easy to modify individual components without breaking others
5. **Real-Time Results**: Decision generated in seconds, not hours
6. **Scalability**: Architecture supports adding more agents or data sources

---

## Q&A Talking Points

**Q: How do agents communicate?**
A: Through standardized MCP servers. Each agent has tools it calls (fetch_profile, calculate_dti, etc.). This decoupling means agents don't need to know about each other directly.

**Q: Can you add more agents?**
A: Yes! The orchestration layer is built to coordinate any number of agents. You could add Geographic Risk Agent, Fraud Detection Agent, etc.

**Q: How is this different from a rules engine?**
A: A rules engine is rigid. This system is AI-powered - agents can reason about edge cases, combine signals intelligently, and explain their logic. The orchestration brings them together into a coherent decision.

**Q: What about bias or fairness?**
A: The explainability trace makes bias detectable. You can see exactly which factors influenced each decision and audit for patterns.

**Q: Can this handle edge cases?**
A: Yes. The anomaly detection in the Risk Agent flags unusual patterns, and the system routes complex cases to manual review rather than making risky auto-denials.

---

## Demo Troubleshooting

**API not responding:**
```bash
# Restart backend
python backend/main.py
```

**Streamlit connection error:**
- Ensure backend is running on `http://localhost:8000`
- Check that `.env` file exists and has valid API key

**Slow response:**
- First request triggers agent initialization (may take 3-5s)
- Subsequent requests are faster

---

## Success Criteria

✅ All three scenarios complete without errors
✅ Decisions are logical and well-reasoned
✅ Execution trace is visible and informative
✅ Live code modification demonstrates modularity
✅ Audience understands multi-agent coordination
