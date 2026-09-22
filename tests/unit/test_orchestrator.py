import pytest
from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from schemas.orchestrator_schema import UserIntent
from agents.orchestrator.orchestrator import FoundryMasterOrchestrator
from agents.orchestrator.routing_rules import IntentRouter


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    # Create test student profile if not exists
    user = db.query(User).filter_by(email="orchestrator_test@example.com").first()
    if not user:
        user = User(email="orchestrator_test@example.com", name="Orchestrator Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = StudentProfile(
            user_id=user.id,
            target_role="Full Stack Engineer",
            target_company_tier="Tier 1 Product",
            graduation_year=2026,
            primary_skills=["Python", "FastAPI", "React"]
        )
        db.add(profile)
        db.commit()
    yield
    db.close()


def test_intent_router_classifications():
    router = IntentRouter(mock_mode=True)

    res_tutor = router.classify("Explain the difference between TCP and UDP with handshake steps")
    assert res_tutor.intent == UserIntent.RAG_TUTOR
    assert res_tutor.extracted_params.get("topic_context") == "Computer Networks"

    res_dsa = router.classify("What is the time complexity of binary search tree insertion?")
    assert res_dsa.intent == UserIntent.RAG_TUTOR
    assert res_dsa.extracted_params.get("topic_context") == "Data Structures and Algorithms"

    res_github = router.classify("Can you inspect github portfolio for user Jiya-garg08?")
    assert res_github.intent == UserIntent.PORTFOLIO_INSPECTION
    assert res_github.extracted_params.get("username") == "Jiya-garg08"

    res_resume = router.classify("Please analyze my resume and check my ATS score for Google JD")
    assert res_resume.intent == UserIntent.RESUME_ANALYSIS

    res_roadmap = router.classify("Generate a 4-week preparation study plan roadmap for backend engineering")
    assert res_roadmap.intent == UserIntent.ROADMAP_PLANNING

    res_diag = router.classify("I want to take a diagnostic assessment test for DSA")
    assert res_diag.intent == UserIntent.DIAGNOSTIC_ASSESSMENT
    assert res_diag.extracted_params.get("topic") == "Data Structures and Algorithms"

    res_gap = router.classify("Show my skill gap analysis and readiness index")
    assert res_gap.intent == UserIntent.SKILL_GAP_ANALYSIS

    res_profile = router.classify("Show my profile details and target role")
    assert res_profile.intent == UserIntent.PROFILE_MANAGEMENT

    res_general = router.classify("Hello, who are you and how can you help me?")
    assert res_general.intent == UserIntent.GENERAL_CONVERSATION


def test_orchestrator_multi_turn_session_tracking():
    orchestrator = FoundryMasterOrchestrator(mock_mode=True)
    session_id = "test-session-multi-turn-001"

    # Turn 1: General Greeting
    resp1 = orchestrator.handle_message(
        session_id=session_id,
        message="Hello! I am preparing for software engineering placements."
    )
    assert resp1.intent == UserIntent.GENERAL_CONVERSATION
    assert "AI Placement Preparation Agent" in resp1.response_text
    assert len(orchestrator.get_session_history(session_id)) == 2  # user + assistant

    # Turn 2: Technical question in DSA domain
    resp2 = orchestrator.handle_message(
        session_id=session_id,
        message="Explain how a binary search tree works and its search complexity"
    )
    assert resp2.intent == UserIntent.RAG_TUTOR
    assert resp2.delegated_agent == "RAGTutorAgent"
    assert len(resp2.citations) > 0
    assert len(orchestrator.get_session_history(session_id)) == 4

    # Turn 3: Follow-up question relying on session context
    session = orchestrator.get_or_create_session(session_id)
    assert session.context.get("active_topic") == "Data Structures and Algorithms"

    resp3 = orchestrator.handle_message(
        session_id=session_id,
        message="Can you explain recursion time complexity?"
    )
    assert resp3.intent == UserIntent.RAG_TUTOR
    assert len(orchestrator.get_session_history(session_id)) == 6


def test_orchestrator_roadmap_delegation():
    orchestrator = FoundryMasterOrchestrator(mock_mode=True)
    session_id = "test-session-roadmap-002"

    resp = orchestrator.handle_message(
        session_id=session_id,
        message="Please generate a 4-week learning roadmap for my placement preparation"
    )
    assert resp.intent == UserIntent.ROADMAP_PLANNING
    assert resp.delegated_agent == "LearningPlannerAgent"
    assert "Week" in resp.response_text
    assert len(resp.suggested_actions) > 0


def test_orchestrator_mcp_bindings_execution():
    orchestrator = FoundryMasterOrchestrator(mock_mode=True)

    # Test executing MCP GitHub Portfolio tool
    gh_res = orchestrator.execute_mcp_tool("get_github_portfolio", username="Jiya-garg08")
    assert gh_res["status"] == "success"
    assert "public_repo_count" in gh_res
    assert "total_stars" in gh_res

    # Test executing non-existent tool
    err_res = orchestrator.execute_mcp_tool("unknown_invalid_tool")
    assert "error" in err_res


def test_orchestrator_session_clear():
    orchestrator = FoundryMasterOrchestrator(mock_mode=True)
    session_id = "test-session-clear-003"

    orchestrator.handle_message(session_id=session_id, message="Hi there!")
    assert len(orchestrator.get_session_history(session_id)) == 2

    orchestrator.clear_session(session_id)
    assert len(orchestrator.get_session_history(session_id)) == 0
