from abc import ABC, abstractmethod
from typing import Dict, Any, List
from shared.utils import get_logger
import time

class BaseMCPServer(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name)
        self.tools: Dict[str, callable] = {}
        self._register_tools()

    @abstractmethod
    def _register_tools(self):
        pass

    def get_tools(self) -> Dict[str, callable]:
        return self.tools

    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {
                "status": "error",
                "error": f"Tool '{tool_name}' not found in {self.name}",
            }

        try:
            start_time = time.time()
            result = self.tools[tool_name](**kwargs)
            execution_time_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "result": result,
                "execution_time_ms": execution_time_ms,
            }
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
            }

    def log_call(self, tool_name: str, kwargs: Dict[str, Any]) -> None:
        self.logger.info(f"Calling tool: {tool_name} with args: {kwargs}")
