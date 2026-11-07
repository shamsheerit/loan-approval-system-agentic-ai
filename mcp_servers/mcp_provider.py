"""Unified MCP Server Provider for all agent tools"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from shared.utils import get_logger
from mcp_servers.applicant_db import ApplicantDBServer
from mcp_servers.risk_rules import RiskRulesServer
from mcp_servers.decision_synthesis import DecisionSynthesisServer
from mcp_servers.notification_system import NotificationSystemServer

logger = get_logger("MCPProvider")


class MCPServerProvider:
    """Centralized MCP-compatible tool provider for all agents.

    This implements the Model Context Protocol (MCP) pattern where all tool
    invocations go through a single registry that coordinates access to
    specialized servers (ApplicantDB, RiskRules, DecisionSynthesis, Notification).

    Agents use this provider instead of instantiating servers directly,
    ensuring consistent tool access patterns and enabling future integration
    with FastMCP or remote MCP servers.
    """

    _instance = None

    def __init__(self):
        self.applicant_db = ApplicantDBServer()
        self.risk_rules = RiskRulesServer()
        self.decision_synthesis = DecisionSynthesisServer()
        self.notification_system = NotificationSystemServer()
        self.logger = logger

    @classmethod
    def get_instance(cls):
        """Get singleton instance of MCP provider"""
        if cls._instance is None:
            cls._instance = cls()
            logger.info("MCP Server Provider initialized")
        return cls._instance

    def call_tool(self, server_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool on a specific MCP server.

        Args:
            server_name: Name of the MCP server ('applicant_db', 'risk_rules', etc.)
            tool_name: Name of the tool to invoke
            **kwargs: Arguments to pass to the tool

        Returns:
            {status: "success", result: ...} or {status: "error", error: ...}
        """
        servers = {
            "applicant_db": self.applicant_db,
            "risk_rules": self.risk_rules,
            "decision_synthesis": self.decision_synthesis,
            "notification_system": self.notification_system,
        }

        if server_name not in servers:
            return {
                "status": "error",
                "error": f"Server '{server_name}' not found. Available: {list(servers.keys())}",
            }

        server = servers[server_name]
        return server.call_tool(tool_name, **kwargs)

    def get_tools_by_server(self, server_name: str) -> Dict[str, callable]:
        """Get all tools from a specific server"""
        servers = {
            "applicant_db": self.applicant_db,
            "risk_rules": self.risk_rules,
            "decision_synthesis": self.decision_synthesis,
            "notification_system": self.notification_system,
        }

        if server_name not in servers:
            return {}

        return servers[server_name].get_tools()

    def get_all_tools(self) -> Dict[str, Dict[str, callable]]:
        """Get all tools across all servers"""
        return {
            "applicant_db": self.applicant_db.get_tools(),
            "risk_rules": self.risk_rules.get_tools(),
            "decision_synthesis": self.decision_synthesis.get_tools(),
            "notification_system": self.notification_system.get_tools(),
        }
