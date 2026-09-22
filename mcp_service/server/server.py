try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from mcp_service.tools.profile_tool import get_student_profile, update_student_target_role
from mcp_service.tools.progress_tool import (
    get_student_performance_summary,
    get_active_learning_roadmap,
    mark_roadmap_item_status
)
from mcp_service.tools.github_tool import get_github_portfolio


def create_mcp_server() -> MCPServer:
    """Instantiate and configure the Placement Preparation MCP Server with sandboxed tools."""
    server = MCPServer("placement-prep-agent")

    # Register Student Profile Tools
    server.tool()(get_student_profile)
    server.tool()(update_student_target_role)

    # Register Performance & Progress Tools
    server.tool()(get_student_performance_summary)
    server.tool()(get_active_learning_roadmap)
    server.tool()(mark_roadmap_item_status)

    # Register GitHub Demonstration Tool
    server.tool()(get_github_portfolio)

    return server


mcp_server = create_mcp_server()

if __name__ == "__main__":
    mcp_server.run()
