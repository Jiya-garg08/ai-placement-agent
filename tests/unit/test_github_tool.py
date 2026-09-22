import pytest
from mcp_service.tools.github_tool import get_github_portfolio
from mcp_service.server.server import create_mcp_server


def test_github_portfolio_mock_mode():
    res = get_github_portfolio("Jiya-garg08", mock_mode=True)
    assert res["status"] == "success"
    assert res["username"] == "Jiya-garg08"
    assert res["public_repo_count"] >= 1
    assert "Python" in res["top_languages"]
    assert len(res["featured_projects"]) >= 2
    assert "name" in res["featured_projects"][0]
    assert "stars" in res["featured_projects"][0]


def test_mcp_server_full_tool_registration():
    server = create_mcp_server()
    assert server is not None
    assert server.name == "placement-prep-agent"
