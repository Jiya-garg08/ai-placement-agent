from pathlib import Path


def test_documentation_files_exist():
    """Verify all key project documentation files exist and have non-empty content."""
    required_docs = [
        "README.md",
        "docs/setup_guide.md",
        "docs/demo_walkthrough.md",
        "docs/architecture.md",
    ]
    for doc in required_docs:
        p = Path(doc)
        assert p.exists(), f"Document {doc} must exist"
        assert p.stat().st_size > 500, f"Document {doc} should contain substantial content"


def test_setup_guide_contains_essential_sections():
    """Verify setup_guide.md details all installation paths and security instructions."""
    content = Path("docs/setup_guide.md").read_text(encoding="utf-8")
    assert "System Requirements" in content
    assert "run_local.bat" in content
    assert "run_local.sh" in content
    assert "docker compose up" in content
    assert "AZURE_MOCK_MODE" in content
    assert "seed_data" in content
    assert "Troubleshooting" in content


def test_demo_walkthrough_covers_ten_pages():
    """Verify demo_walkthrough.md scripts all 10 stages of the student journey."""
    content = Path("docs/demo_walkthrough.md").read_text(encoding="utf-8")
    pages = [
        "1_📊_Dashboard",
        "2_👤_Student_Profile",
        "3_📄_Resume_JD_Analysis",
        "4_📝_Diagnostic_Assessment",
        "5_🔍_Skill_Gap",
        "6_📅_Learning_Plan",
        "7_🤖_RAG_Tutor",
        "8_💻_Practice",
        "9_📈_Performance",
        "10_🎯_Next_Best_Action"
    ]
    for page in pages:
        assert page in content, f"Demo walkthrough must cover {page}"


def test_architecture_documentation_covers_mcp_and_rag():
    """Verify architecture.md outlines Foundry orchestrator, MCP, and RAG retrieval."""
    content = Path("docs/architecture.md").read_text(encoding="utf-8")
    assert "Microsoft Foundry" in content
    assert "Model Context Protocol" in content
    assert "Azure AI Search" in content
    assert "SQLite" in content
    assert "PII Sanitization" in content
