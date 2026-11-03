# Setup Instructions - Agentic AI Loan Approval System

## Prerequisites

- Python 3.8+
- pip package manager
- Anthropic API key (for future Claude integration)
- ~2GB disk space

## Installation

### 1. Clone or Navigate to Project

```bash
cd /home/ubuntu/loan-approval-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env  # If template exists
# Edit .env and add your ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Running the System

### Option A: Full System (Recommended for Demo)

**Terminal 1 - Start FastAPI Backend**:
```bash
python backend/main.py
# Server starts on http://localhost:8000
```

**Terminal 2 - Start Streamlit UI**:
```bash
streamlit run ui/streamlit_app.py
# UI opens on http://localhost:8501
```

### Option B: Backend Only (API Testing)

```bash
python backend/main.py
```

Then test endpoints with curl:
```bash
# Submit application
curl -X POST http://localhost:8000/api/loan/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
    "applicant_profile": {
      "age": 35,
      "income": 60000,
      "employment_type": "salaried"
    },
    "credit_score": 750,
    "loan_amount": 100000,
    "tenure_months": 60,
    "existing_liabilities": 10000,
    "location": "New York"
  }'

# Returns:
{
  "application_id": "APP-ABC123DEF456",
  "status": "submitted",
  "decision": null
}

# Check status
curl http://localhost:8000/api/loan/status/APP-ABC123DEF456

# Get decision (when ready)
curl http://localhost:8000/api/loan/decision/APP-ABC123DEF456

# Health check
curl http://localhost:8000/api/health
```

### Option C: Workflow Only (Testing)

```bash
python tests/test_workflow.py
```

Output shows test scenarios and decisions.

## Project Structure

```
loan-approval-system/
├── backend/                 # FastAPI application
│   ├── app.py              # Main application
│   ├── main.py             # Entry point
│   └── schemas.py          # Request/response models
├── ui/                      # Streamlit frontend
│   └── streamlit_app.py    # UI application
├── orchestration/           # LangGraph workflow
│   └── loan_approval_workflow.py  # Orchestration logic
├── agents/                  # Domain-specific agents
│   ├── applicant_profile_agent.py
│   ├── financial_risk_agent.py
│   ├── loan_decision_agent.py
│   └── compliance_orchestrator_agent.py
├── mcp_servers/            # MCP server implementations
│   ├── base_server.py
│   ├── applicant_db.py
│   ├── risk_rules.py
│   ├── decision_synthesis.py
│   └── notification_system.py
├── shared/                  # Shared models and utilities
│   ├── models.py           # Pydantic models
│   └── utils.py            # Helper functions
├── tests/                   # Test suite
│   └── test_workflow.py    # Workflow tests
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md     # Architecture details
│   ├── SETUP.md           # This file
│   └── DEMO_SCRIPT.md     # Demo walkthrough
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .gitignore              # Git ignore patterns
└── README.md               # Project overview
```

## Configuration

### Environment Variables (.env)

```
ANTHROPIC_API_KEY=sk-ant-...        # Your API key
ENVIRONMENT=development              # development | staging | production
DEBUG=True                           # Enable debug logging
LOG_LEVEL=INFO                       # INFO | DEBUG | WARNING | ERROR
API_PORT=8000                        # FastAPI port
STREAMLIT_PORT=8501                  # Streamlit port
```

### Modifying Decision Rules

To adjust loan decision thresholds:

1. **Edit DTI thresholds** (`mcp_servers/risk_rules.py`):
```python
self.dti_thresholds = {
    "low": (0, 0.30),           # Adjust these ranges
    "moderate": (0.30, 0.43),
    "high": (0.43, 0.50),
    "very_high": (0.50, float("inf")),
}
```

2. **Edit credit score thresholds** (`mcp_servers/risk_rules.py`):
```python
self.credit_score_thresholds = {
    "excellent": (750, 850),    # Adjust these ranges
    "good": (700, 749),
    "fair": (650, 699),
    "poor": (600, 649),
    "very_poor": (300, 599),
}
```

3. **Edit decision weights** (`mcp_servers/decision_synthesis.py`):
```python
combined_risk_score = (
    (credit_risk_score * 0.4) +      # Adjust weights (must sum to ~1.0)
    ((dti_ratio * 100) * 0.3) +
    ((100 - income_stability) * 0.3)
)
```

4. **Edit classification thresholds** (`mcp_servers/decision_synthesis.py`):
```python
if risk_score >= 70:                 # Adjust thresholds
    return DecisionClassification.REJECTED
elif risk_score >= 40:
    return DecisionClassification.MANUAL_REVIEW
else:
    return DecisionClassification.APPROVED
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused" when accessing API from Streamlit

**Solution**:
- Ensure FastAPI backend is running
- Check that API_PORT in .env matches backend startup
- Verify firewall isn't blocking localhost:8000

### Issue: Streamlit says "API connection error"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Restart backend if needed
python backend/main.py
```

### Issue: Tests fail with import errors

**Solution**:
```bash
# From project root
cd /home/ubuntu/loan-approval-system
python tests/test_workflow.py
```

### Issue: Decision takes >5 seconds

**Solution**:
- First request may be slow due to initialization
- Subsequent requests should be faster (~1 second)
- Check system resources (CPU, memory)

## Testing

### Run All Tests

```bash
python tests/test_workflow.py
```

### Run Specific Test

```bash
python -m pytest tests/test_workflow.py::test_workflow_approved_applicant -v
```

### Manual Testing via API

```bash
# Test approved scenario
curl -X POST http://localhost:8000/api/loan/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST-APPROVED",
    "applicant_profile": {"age": 35, "income": 60000, "employment_type": "salaried"},
    "credit_score": 750,
    "loan_amount": 100000,
    "tenure_months": 60,
    "existing_liabilities": 10000,
    "location": "New York"
  }'

# Test rejection scenario
curl -X POST http://localhost:8000/api/loan/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST-REJECTED",
    "applicant_profile": {"age": 28, "income": 25000, "employment_type": "self_employed"},
    "credit_score": 550,
    "loan_amount": 200000,
    "tenure_months": 36,
    "existing_liabilities": 50000,
    "location": "Los Angeles"
  }'
```

## Development

### Adding a New Agent

1. Create `agents/new_agent.py`:
```python
from shared.utils import get_logger

class NewAgent:
    def __init__(self):
        self.name = "NewAgent"
        self.logger = get_logger(self.name)
        # Initialize MCP server
    
    def analyze(self, data):
        # Implement analysis logic
        return {"status": "success", "output": {...}}
```

2. Register in `orchestration/loan_approval_workflow.py`:
```python
self.new_agent = NewAgent()
```

3. Add workflow step:
```python
def _run_new_agent(self, state):
    result = self.new_agent.analyze(state["application"])
    state["new_analysis"] = result["output"]
    return state
```

4. Integrate in workflow graph

### Adding a New MCP Server

1. Create `mcp_servers/new_server.py`:
```python
from .base_server import BaseMCPServer

class NewServer(BaseMCPServer):
    def __init__(self):
        super().__init__("NewServer")
    
    def _register_tools(self):
        self.tools["tool_name"] = self.tool_name
    
    def tool_name(self, param):
        return {"result": "..."}
```

2. Register in agent that uses it

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "backend/main.py"]
```

```bash
docker build -t loan-approval-system .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY="..." loan-approval-system
```

### Cloud Deployment (AWS/GCP/Azure)

- Package as Docker container
- Deploy to Kubernetes or serverless platform
- Use managed database for case history
- Set up CDN for Streamlit frontend
- Enable HTTPS/TLS

## Performance Optimization

### Caching

Currently uses in-memory cache. For production:
```python
# Use Redis
import redis
cache = redis.Redis(host='localhost', port=6379)
```

### Database

Currently uses mock data. For production:
```python
# Use PostgreSQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:password@localhost/loans')
```

### Load Balancing

Deploy multiple API instances behind load balancer:
```
Load Balancer → Instance 1 → API
               → Instance 2 → API
               → Instance 3 → API
```

## Monitoring

### Logging

Logs printed to console and can be redirected:
```bash
python backend/main.py > backend.log 2>&1 &
```

### Metrics

Add Prometheus metrics:
```python
from prometheus_client import Counter, Histogram

decision_counter = Counter('decisions_total', 'Total decisions by classification')
decision_latency = Histogram('decision_latency_seconds', 'Decision latency')
```

### Alerting

Set up alerts for:
- Error rate > 5%
- Latency > 5s
- API down
- Database connection issues

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review architecture documentation
3. Check test cases for examples
4. Review logs for error details
