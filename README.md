# Agentic AI Intelligent Loan Approval System

A Multi-Agent Agentic AI system for automated loan application analysis and approval classification.

## Architecture

- **Presentation Layer**: Streamlit chatbot UI
- **API Gateway**: FastAPI REST endpoints
- **Orchestration**: LangGraph workflow engine
- **Agents**: 4 domain-specific agents (Profile, Risk, Decision, Compliance)
- **Communication**: FastMCP servers for standardized agent communication

## Quick Start

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run

**FastAPI Backend:**
```bash
python backend/main.py
```

**Streamlit UI:**
```bash
streamlit run ui/streamlit_app.py
```

## Project Structure

- `shared/` - Shared data models and utilities
- `mcp-servers/` - MCP server implementations
- `agents/` - Domain-specific agent implementations
- `orchestration/` - LangGraph workflow orchestration
- `backend/` - FastAPI microservice
- `ui/` - Streamlit frontend
- `tests/` - Test suite

## Documentation

- `docs/ARCHITECTURE.md` - System architecture details
- `docs/SETUP.md` - Detailed setup instructions
- `docs/DEMO_SCRIPT.md` - Demo walkthrough guide
