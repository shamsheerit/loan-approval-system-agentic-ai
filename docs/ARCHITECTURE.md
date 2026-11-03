# Agentic AI Loan Approval System - Architecture Documentation

## System Overview

The Agentic AI Intelligent Loan Approval System is a multi-agent microservices architecture designed to automate loan application analysis and decision classification. The system uses independent, domain-specific agents that collaborate through a standardized orchestration layer to provide explainable, auditable loan decisions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│            (Streamlit Web Application)                       │
│  - Interactive form for loan application submission          │
│  - Real-time decision visualization                          │
│  - Execution trace display for explainability               │
└────────────────────┬────────────────────────────────────────┘
                     │ REST HTTP/Async
                     │
┌────────────────────▼────────────────────────────────────────┐
│              API GATEWAY LAYER                               │
│           (FastAPI Microservice)                             │
│  - POST /api/loan/submit → Receives applications            │
│  - GET /api/loan/status/{id} → Polls processing status      │
│  - GET /api/loan/decision/{id} → Retrieves final decision   │
│  - Async processing with in-memory cache                    │
└────────────────────┬────────────────────────────────────────┘
                     │ Python Objects
                     │
┌────────────────────▼────────────────────────────────────────┐
│         ORCHESTRATION LAYER (LangGraph)                      │
│       Loan Approval Workflow Coordinator                     │
│                                                               │
│  Graph State: application, profile_analysis, risk_analysis,  │
│               final_decision, execution_trace                │
│                                                               │
│  Workflow Steps:                                             │
│   1. validate_input → Validates application data            │
│   2. run_profile_agent ─┐                                   │
│                         ├→ run_decision_agent →             │
│   3. run_risk_agent ────┘  run_compliance_agent             │
│   4. format_response                                         │
└──┬──────┬──────────┬────────────┬───────────────────────────┘
   │      │          │            │
┌──▼──┐ ┌─▼─────┐ ┌─▼──────────┐ ┌──▼─────────┐
│ APP │ │ FIN   │ │   LOAN     │ │COMPLIANCE  │
│PROF │ │ RISK  │ │DECISION    │ │ORCHESTRATOR│
│AGEN │ │AGENT  │ │AGENT       │ │AGENT       │
└──┬──┘ └─┬─────┘ └─┬──────────┘ └──┬─────────┘
   │      │         │               │
   └──────┼─────────┼───────────────┘
          │         │
          └────┬────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│     COMMUNICATION LAYER (MCP Servers)                        │
│                                                               │
│  Standardized tool interface for agent-service interaction  │
└──┬──────┬──────────┬──────────┬──────────────────────────────┘
   │      │          │          │
┌──▼──┐ ┌─▼─────┐ ┌─▼──────┐ ┌─▼──────────┐
│APPL │ │RISK   │ │DECISION│ │NOTIF.      │
│ICNT │ │RULES  │ │SYNTHES.│ │SYSTEM      │
│ DB  │ │DB     │ │SERVER  │ │SERVER      │
└─────┘ └───────┘ └────────┘ └────────────┘
```

## Layer Descriptions

### 1. Presentation Layer (Streamlit)

**File**: `ui/streamlit_app.py`

**Responsibilities**:
- Provides interactive web UI for loan application submission
- Displays decision results with visual indicators
- Shows execution trace for transparency
- Manages session state for application history

**Key Features**:
- Form with all loan application fields
- Real-time status checking with polling
- Decision visualization (color-coded: green/red/orange)
- Expandable debug section for execution trace
- Responsive two-column layout

### 2. API Gateway Layer (FastAPI)

**File**: `backend/app.py`, `backend/schemas.py`

**Responsibilities**:
- Receives and validates loan applications
- Routes requests to orchestration layer
- Manages async processing with in-memory cache
- Provides status polling endpoints

**Endpoints**:
```
POST /api/loan/submit
  - Accepts: LoanApplicationRequest
  - Returns: ApplicationStatusResponse with application_id
  - Triggers async workflow processing

GET /api/loan/status/{application_id}
  - Returns: ApplicationStatusResponse
  - Status: submitted | processing | completed | error

GET /api/loan/decision/{application_id}
  - Returns: LoanDecisionResponse (only when completed)
  - Includes full decision with factors and trace

POST/GET /api/health
  - Returns: HealthCheckResponse
```

**Request Schema**:
```python
LoanApplicationRequest:
  - applicant_id: str
  - applicant_profile:
      - age: int (18-100)
      - income: float
      - employment_type: "salaried" | "self_employed" | "business"
  - credit_score: int (300-850)
  - loan_amount: float
  - tenure_months: int
  - existing_liabilities: float
  - location: str
```

### 3. Orchestration Layer (LangGraph)

**File**: `orchestration/loan_approval_workflow.py`

**Responsibilities**:
- Coordinates multi-agent workflow
- Manages state transitions
- Handles error scenarios
- Records execution trace for audit trail

**Workflow State**:
```python
{
  "application": LoanApplication,           # Input
  "profile_analysis": ProfileAnalysis,      # Agent output
  "risk_analysis": RiskAnalysis,            # Agent output
  "final_decision": DecisionOutcome,        # Agent output
  "compliance_action": dict,                # Agent output
  "execution_trace": List[TraceEntry],      # All steps
  "errors": List[str],                      # Any errors
}
```

**Execution Flow**:
1. **validate_input** → Check application data completeness
2. **run_profile_agent** → Analyze applicant (parallel)
3. **run_risk_agent** → Assess financial risk (parallel)
4. **run_decision_agent** → Synthesize decision
5. **run_compliance_agent** → Execute post-decision actions
6. **format_response** → Structure final output

**Parallelization**: Profile and Risk agents execute simultaneously, improving latency from ~2s to ~1s for typical cases.

### 4. Agent Layer

Each agent has a single responsibility and uses MCP servers to access data/services.

#### 4.1 Applicant Profile Agent

**File**: `agents/applicant_profile_agent.py`

**Responsibility**: Analyze applicant credentials, employment history, income stability

**Workflow**:
1. Call `ApplicantDBServer.fetch_applicant_profile()`
2. Call `ApplicantDBServer.get_income_stability_score()`
3. Assess employment risk based on employment type
4. Validate application completeness

**Output** (ProfileAnalysis):
```python
{
  "income_stability_score": 85,        # 0-100
  "employment_risk": "low",            # low | moderate | high
  "credit_history_summary": "...",
  "application_completeness_flags": [] # Any missing fields
}
```

#### 4.2 Financial Risk Agent

**File**: `agents/financial_risk_agent.py`

**Responsibility**: Quantify financial risk through multiple metrics and anomaly detection

**Calculations**:
1. **DTI Ratio** = Monthly Liabilities / Monthly Income
   - Low: 0-0.30, Moderate: 0.30-0.43, High: 0.43-0.50, Very High: >0.50

2. **Credit Risk Score**
   - Excellent (750-850): 10 points
   - Good (700-749): 25 points
   - Fair (650-699): 50 points
   - Poor (600-649): 75 points
   - Very Poor (300-599): 90 points

3. **Loan Amount Risk** = Loan Amount / Annual Income
   - Low: <1.5x, Moderate: 1.5-3x, High: 3-5x, Very High: >5x

4. **Anomaly Detection**
   - High-risk profile: Low credit score + High DTI
   - Extreme loan-to-income
   - Age mismatch with loan ratio
   - Self-employed with low credit

**Output** (RiskAnalysis):
```python
{
  "debt_to_income_ratio": 0.35,
  "credit_score_risk_level": "good",
  "loan_amount_risk": "moderate",
  "anomalies_detected": [],
  "reasoning": "...",
  "credit_risk_score": 25,
  "anomaly_count": 0
}
```

#### 4.3 Loan Decision Agent

**File**: `agents/loan_decision_agent.py`

**Responsibility**: Synthesize profile and risk analysis into final classification

**Decision Logic**:
1. Compute combined risk score (0-100):
   ```
   risk_score = (credit_risk * 0.4) + (dti * 0.3) + (income_instability * 0.3)
   + anomaly_penalty
   ```

2. Classify:
   - Risk >= 70: **REJECTED**
   - Risk >= 40: **REQUIRES_MANUAL_REVIEW**
   - Risk < 40: **APPROVED**

3. Calculate confidence:
   - Base 0.85, adjusted by stability and anomalies
   - Reduced if risk is borderline (35-65)

4. Extract decision factors (top 2-4):
   - Income stability quality
   - DTI assessment
   - Credit profile
   - Anomalies (if any)

**Output** (DecisionOutcome):
```python
{
  "classification": "APPROVED",         # Enum
  "risk_score": 23.5,                  # 0-100
  "confidence_level": 0.72,            # 0-1
  "decision_factors": [...],           # List[str]
  "explanation": "Application approved. Risk assessment...",
  "case_id": "CASE-59EAAFCA0994",
  "timestamp": "2026-11-03T13:58:00.875Z"
}
```

#### 4.4 Compliance & Action Orchestrator Agent

**File**: `agents/compliance_orchestrator_agent.py`

**Responsibility**: Execute post-decision actions (notifications, logging, audit trail)

**Actions**:
1. Log case in audit trail with decision details
2. Send notification to applicant
3. Record case ID for follow-up

**Output**:
```python
{
  "case_id": "CASE-59EAAFCA0994",
  "action_taken": "NOTIFICATION_SENT_AND_LOGGED",
  "notification_sent": true,
  "case_logged": true,
  "recipient": "APP001@example.com",
  "timestamp": "2026-11-03T13:58:00.876Z"
}
```

### 5. Communication Layer (MCP Servers)

**Base File**: `mcp_servers/base_server.py`

Each MCP server implements a standardized interface:
- `get_tools()` → Returns available tools
- `call_tool(tool_name, **kwargs)` → Executes tool with error handling
- Consistent response format with execution time tracking

#### 5.1 ApplicantDB Server

**File**: `mcp_servers/applicant_db.py`

**Tools**:
- `fetch_applicant_profile(applicant_id)` → Returns profile + history
- `validate_application_completeness(applicant_id)` → Returns flags
- `get_income_stability_score(applicant_id)` → Returns score (0-100)

**Data Source**: Mock in-memory database (expandable to PostgreSQL/MongoDB)

#### 5.2 RiskRulesDB Server

**File**: `mcp_servers/risk_rules.py`

**Tools**:
- `calculate_dti_ratio(monthly_income, monthly_liabilities)` → Returns ratio + classification
- `assess_credit_risk(credit_score)` → Returns risk level + score
- `evaluate_loan_amount_risk(loan_amount, annual_income, tenure_months)` → Returns risk level
- `detect_anomalies(credit_score, dti_ratio, loan_to_income, age, employment_type)` → Returns anomalies list

**Rule Configuration**: Configurable thresholds for DTI, credit scores, loan-to-income ratios

#### 5.3 DecisionSynthesis Server

**File**: `mcp_servers/decision_synthesis.py`

**Tools**:
- `synthesize_decision(profile_analysis, risk_analysis)` → Returns classification + reasoning

**Logic**: Combines signals from profile and risk analysis into coherent decision

#### 5.4 NotificationSystem Server

**File**: `mcp_servers/notification_system.py`

**Tools**:
- `send_notification(case_id, decision, applicant_email)` → Sends decision notification
- `log_case(case_id, decision, risk_score, decision_factors, applicant_id)` → Logs to audit trail
- `get_case_history(limit)` → Returns recent cases

**Data Source**: In-memory case log (expandable to persistent database)

## Data Models

**File**: `shared/models.py`

### Core Models

```python
# Enums
EmploymentType: SALARIED | SELF_EMPLOYED | BUSINESS
DecisionClassification: APPROVED | REJECTED | REQUIRES_MANUAL_REVIEW

# Input
LoanApplication:
  - applicant_id: str
  - applicant_profile: ApplicantProfile
  - credit_score: int (300-850)
  - loan_amount: float
  - tenure_months: int
  - existing_liabilities: float
  - location: str
  - timestamp: datetime

# Agent Outputs
ProfileAnalysis:
  - income_stability_score: float (0-100)
  - employment_risk: str
  - credit_history_summary: str
  - application_completeness_flags: List[str]

RiskAnalysis:
  - debt_to_income_ratio: float
  - credit_score_risk_level: str
  - loan_amount_risk: str
  - anomalies_detected: List[str]
  - reasoning: str

# Final Output
DecisionOutcome:
  - classification: DecisionClassification
  - risk_score: float (0-100)
  - confidence_level: float (0-1)
  - decision_factors: List[str]
  - explanation: str
  - case_id: str
  - timestamp: datetime
```

## Key Design Decisions

### 1. **Agent Independence**
Each agent has a single responsibility and doesn't depend on other agents. This enables:
- Independent testing and development
- Easy replacement/upgrade of individual agents
- Parallel execution for improved latency

### 2. **Standardized Communication (MCP)**
Agents don't call each other directly; they use standardized tools via MCP servers. Benefits:
- Loose coupling
- Easy to add new data sources or services
- Clear API contracts
- Testability

### 3. **Parallel Execution**
Profile and Risk agents run simultaneously in LangGraph, reducing latency by ~50%.

### 4. **Explicit Decision Logic**
Decision is made through explicit calculations, not black-box ML. Benefits:
- Explainability (can trace every factor)
- Auditability
- Regulatory compliance
- Easy to adjust thresholds

### 5. **Audit Trail**
Every step is logged in execution trace for compliance and debugging.

### 6. **Async Processing**
FastAPI uses async/await for responsive UI while processing runs in background.

## Execution Flow Example

```
User submits: 
  Applicant: APP001, Age: 35, Income: 60k, Credit: 750, 
  Loan: 100k, DTI: 0.2, Location: NY

1. API validates input
2. Creates LoanApplication object
3. Triggers LoanApprovalWorkflow.run()

4. Workflow validates input → PASSED

5. In parallel:
   - ProfileAgent.analyze()
     - Fetches profile: income_stability=85, employment_risk=low
     - Returns ProfileAnalysis

   - RiskAgent.analyze()
     - Calculates DTI: 0.2 (low)
     - Assesses credit: 750 (excellent) → risk_score=10
     - Evaluates loan_to_income: 1.67x (low)
     - Detects anomalies: none
     - Returns RiskAnalysis

6. DecisionAgent.decide()
   - Combines: income_stability=85, credit_risk=10, DTI=0.2
   - Computes: risk_score = (10*0.4 + 20*0.3 + 15*0.3) = 15
   - Classifies: 15 < 40 → APPROVED
   - Confidence: 0.85 * 0.85 * 1.0 = 0.72
   - Factors: ["Strong income stability", "Favorable debt-to-income ratio"]
   - Returns DecisionOutcome

7. ComplianceAgent.execute()
   - Logs case: CASE-59EAAFCA0994 with all details
   - Sends notification to APP001@example.com
   - Returns action summary

8. Response formatted with execution trace showing all steps

Total time: ~1 second (profile + risk parallel)
```

## Scalability Considerations

### Current Implementation
- In-memory caching (suitable for demo/POC)
- Single instance
- Mock data sources

### Production Enhancements
1. **Persistent Database**
   - Replace in-memory cache with Redis for distributed caching
   - Use PostgreSQL for case history and audit logs

2. **Microservices Deployment**
   - Deploy each MCP server independently
   - Use containerization (Docker)
   - Orchestrate with Kubernetes

3. **Enhanced Agents**
   - Add fraud detection agent
   - Add geographic risk agent
   - Integrate external data sources (credit bureaus, employment verification)

4. **Monitoring & Observability**
   - Add Prometheus metrics
   - Implement distributed tracing
   - Real-time alerting

5. **Advanced Features**
   - Feedback loop for continuous model improvement
   - A/B testing for decision rules
   - Explainability reports generation

## Testing Strategy

**Test Files**: `tests/test_workflow.py`

**Test Scenarios**:
1. **Clear Approval**: High credit, low DTI, stable employment
2. **Clear Rejection**: Low credit, high DTI, high loan-to-income
3. **Manual Review**: Borderline metrics, some anomalies

**Coverage**:
- Unit tests for individual agents
- Integration tests for workflow
- End-to-end tests including API

All tests validate:
- Correct classification
- Risk scores in valid range (0-100)
- Confidence levels in valid range (0-1)
- Decision factors present and relevant
- Execution trace complete

## Performance Characteristics

- **Typical latency**: 0.9-1.2 seconds end-to-end
- **Profile agent**: ~0.3ms
- **Risk agent**: ~0.3ms (parallel with Profile)
- **Decision agent**: ~0.1ms
- **Compliance agent**: ~0.2ms
- **API overhead**: ~0.1ms

Bottleneck: LLM calls (if using Claude API for advanced agents in future)

## Security Considerations

1. **Input Validation**: All fields validated with Pydantic
2. **API Rate Limiting**: Can be added via FastAPI middleware
3. **Audit Trail**: Complete trace of all decisions for compliance
4. **Error Handling**: Graceful error responses, no stack traces exposed
5. **Sensitive Data**: Applicant data handled with care (can add encryption at rest)
