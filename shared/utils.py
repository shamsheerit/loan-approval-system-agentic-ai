import logging
import uuid
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def generate_case_id() -> str:
    return f"CASE-{uuid.uuid4().hex[:12].upper()}"

def generate_application_id() -> str:
    return f"APP-{uuid.uuid4().hex[:12].upper()}"

def format_timestamp(dt: datetime = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()

def create_error_response(error_message: str, agent_name: str) -> Dict[str, Any]:
    return {
        "agent_name": agent_name,
        "status": "error",
        "output": {},
        "error": error_message,
        "execution_time_ms": 0,
    }
