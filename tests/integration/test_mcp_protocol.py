import pytest
from mcp_service.server.server import create_mcp_server
from tests.mocks.mock_mcp_client import MockMCPClient
from app.utils.seed_demo_student import seed_demo_candidate
from database.database import init_db, SessionLocal
from database.models.student import User


@pytest.fixture(scope="module")
def setup_mcp_student():
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email="jiya.garg@example.com").first()
        if user and user.profile:
            return int(user.profile.id)
        profile = seed_demo_candidate(session=db)
        return int(profile.id)
    finally:
        db.close()


def test_mcp_server_initialization():
    """Verify FastMCP/MCPServer initializes with all registered placement tools."""
    server = create_mcp_server()
    assert server is not None
    assert server.name == "placement-prep-agent"


def test_mock_mcp_client_tool_listing():
    """Verify mock MCP client lists all 6 available tools with valid names and descriptions."""
    client = MockMCPClient()
    tools = client.list_tools()
    assert len(tools) == 6

    tool_names = [t["name"] for t in tools]
    assert "get_student_profile" in tool_names
    assert "update_student_target_role" in tool_names
    assert "get_student_performance_summary" in tool_names
    assert "get_active_learning_roadmap" in tool_names
    assert "mark_roadmap_item_status" in tool_names
    assert "get_github_portfolio" in tool_names


def test_mcp_call_get_student_profile(setup_mcp_student):
    """Verify calling get_student_profile via MCP protocol returns structured candidate telemetry."""
    client = MockMCPClient()
    pid = setup_mcp_student
    res = client.call_tool("get_student_profile", {"student_id": pid})
    assert res["isError"] is False
    assert res["structuredContent"]["status"] == "success"
    assert res["structuredContent"]["name"] == "Jiya Garg"


def test_mcp_call_github_portfolio():
    """Verify calling get_github_portfolio via MCP protocol returns repository metrics."""
    client = MockMCPClient()
    res = client.call_tool("get_github_portfolio", {"username": "Jiya-garg08", "mock_mode": True})
    assert res["isError"] is False
    content = res["structuredContent"]
    assert content["status"] == "success"
    assert content["public_repo_count"] >= 1
    assert "Python" in content["top_languages"]


def test_mcp_call_invalid_tool():
    """Verify calling an unregistered tool returns isError=True."""
    client = MockMCPClient()
    res = client.call_tool("non_existent_tool", {})
    assert res["isError"] is True
    assert "not found" in res["content"][0]["text"].lower()
