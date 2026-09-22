"""Mock MCP stdio client simulation for testing Model Context Protocol contracts."""

from typing import Dict, Any, List, Optional
from mcp_service.tools.profile_tool import get_student_profile, update_student_target_role
from mcp_service.tools.progress_tool import (
    get_student_performance_summary,
    get_active_learning_roadmap,
    mark_roadmap_item_status
)
from mcp_service.tools.github_tool import get_github_portfolio


class MockMCPClient:
    """Simulates an MCP Client issuing JSON-RPC calls against registered server tools."""

    def __init__(self):
        self.registered_tools = {
            "get_student_profile": get_student_profile,
            "update_student_target_role": update_student_target_role,
            "get_student_performance_summary": get_student_performance_summary,
            "get_active_learning_roadmap": get_active_learning_roadmap,
            "mark_roadmap_item_status": mark_roadmap_item_status,
            "get_github_portfolio": get_github_portfolio
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Simulate MCP tools/list request."""
        tools = []
        for name, fn in self.registered_tools.items():
            doc = fn.__doc__ or "MCP Tool"
            tools.append({
                "name": name,
                "description": doc.strip().split("\n")[0],
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            })
        return tools

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate MCP tools/call request."""
        if name not in self.registered_tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{name}' not found."}]
            }

        fn = self.registered_tools[name]
        kwargs = arguments or {}
        try:
            result = fn(**kwargs)
            return {
                "isError": False,
                "content": [{"type": "text", "text": str(result)}],
                "structuredContent": result
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": str(e)}]
            }
