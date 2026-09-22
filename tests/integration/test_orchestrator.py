import time
import pytest
from database.database import init_db, SessionLocal
from database.models.student import User, StudentProfile
from schemas.orchestrator_schema import UserIntent
from agents.orchestrator.orchestrator import FoundryMasterOrchestrator
from agents.orchestrator.agent_registry import AgentRegistry
from agents.common.error_handler import RateLimiter, ResponseCache, safe_agent_call


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    user = db.query(User).filter_by(email="swarm_test@example.com").first()
    if not user:
        user = User(email="swarm_test@example.com", name="Swarm Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = StudentProfile(
            user_id=user.id,
            target_role="Software Development Engineer (SDE)",
            target_company_tier="Tier 1 Product",
            graduation_year=2026,
            primary_skills=["Python", "DSA", "SQL"]
        )
        db.add(profile)
        db.commit()
    yield
    db.close()


def test_agent_registry_swarm_capabilities():
    """Verify subagent registry tracks all swarm components with correct intents and roles."""
    registry = AgentRegistry(mock_mode=True)
    agents = registry.list_agents()
    agent_names = [a.name for a in agents]

    assert "ResumeAnalysisAgent" in agent_names
    assert "AssessmentService" in agent_names
    assert "SkillGapService" in agent_names
    assert "LearningPlannerAgent" in agent_names
    assert "RAGTutorAgent" in agent_names

    # Check intent mapping
    assert registry.get_agent_for_intent(UserIntent.RAG_TUTOR) == "RAGTutorAgent"
    assert registry.get_agent_for_intent(UserIntent.ROADMAP_PLANNING) == "LearningPlannerAgent"
    assert registry.get_agent_for_intent(UserIntent.RESUME_ANALYSIS) == "ResumeAnalysisAgent"

    # Health check report
    health = registry.health_check_all()
    assert all(status == "HEALTHY" for status in health.values())


def test_safety_boundary_timeout_protection():
    """Verify safe_agent_call catches lagging or hanging calls and triggers graceful fallback."""
    def hanging_function():
        time.sleep(2.0)
        return "finished"

    def fallback_function():
        return "safe_offline_output"

    # Execution with 0.1s timeout should trigger fallback immediately
    result, is_fallback, notice = safe_agent_call(
        hanging_function,
        fallback_func=fallback_function,
        timeout_seconds=0.1
    )

    assert is_fallback is True
    assert result == "safe_offline_output"
    assert "timed out" in notice.lower()


def test_safety_boundary_rate_limiting_guard():
    """Verify rate limiter blocks burst requests exceeding limits and serves cached response."""
    limiter = RateLimiter(max_requests_per_minute=2, max_tokens_per_minute=1000)
    cache = ResponseCache()
    cache.set("cached_key_001", "cached_answer_content")

    # 1st call - allowed
    res1, is_fb1, _ = safe_agent_call(
        lambda: "call_1",
        cache_key="cached_key_001",
        rate_limiter=limiter,
        cache=cache
    )
    assert res1 == "call_1"
    assert is_fb1 is False

    # 2nd call - allowed
    res2, is_fb2, _ = safe_agent_call(
        lambda: "call_2",
        cache_key="cached_key_001",
        rate_limiter=limiter,
        cache=cache
    )
    assert res2 == "call_2"
    assert is_fb2 is False

    # 3rd call - exceeds 2 requests/min limit! Must trip rate limiter and serve cache
    res3, is_fb3, notice3 = safe_agent_call(
        lambda: "call_3",
        cache_key="cached_key_001",
        rate_limiter=limiter,
        cache=cache
    )
    assert is_fb3 is True
    assert res3 == "call_2"
    assert "rate limit exceeded" in notice3.lower()


def test_orchestrator_resilient_error_degradation():
    """Verify orchestrator gracefully handles subagent exceptions without crashing."""
    class CrashingTutor:
        def answer_query(self, req):
            raise ConnectionError("Simulated Azure OpenAI connection refused")

    orchestrator = FoundryMasterOrchestrator(
        tutor_agent=CrashingTutor(),
        mock_mode=True
    )
    session_id = "test-session-crash-001"

    # Prompt that routes to RAG Tutor
    resp = orchestrator.handle_message(
        session_id=session_id,
        message="Explain database ACID properties and transactions"
    )

    assert resp.intent == UserIntent.RAG_TUTOR
    assert "⚠️" in resp.response_text or "connection" in resp.response_text.lower()
    assert len(resp.citations) == 0


def test_end_to_end_multi_agent_swarm_flow():
    """Full integration journey: Greeting -> Tutor -> Roadmap -> Portfolio -> Profile."""
    orchestrator = FoundryMasterOrchestrator(mock_mode=True)
    session_id = "test-session-swarm-flow-001"

    # 1. Greeting
    r1 = orchestrator.handle_message(session_id, "Hi! I want to prepare for campus placements.")
    assert r1.intent == UserIntent.GENERAL_CONVERSATION
    assert "AI Placement Preparation Agent" in r1.response_text

    # 2. Technical question
    r2 = orchestrator.handle_message(session_id, "Explain how a binary search tree works and its search complexity")
    assert r2.intent == UserIntent.RAG_TUTOR
    assert len(r2.citations) > 0

    # 3. Roadmap generation
    r3 = orchestrator.handle_message(session_id, "Generate my 4-week preparation study plan")
    assert r3.intent == UserIntent.ROADMAP_PLANNING
    assert "Week" in r3.response_text

    # 4. GitHub portfolio inspection
    r4 = orchestrator.handle_message(session_id, "Inspect github profile for Jiya-garg08")
    assert r4.intent == UserIntent.PORTFOLIO_INSPECTION
    assert "GitHub Portfolio Analysis" in r4.response_text

    # 5. Profile check
    r5 = orchestrator.handle_message(session_id, "Show my student profile and target role")
    assert r5.intent == UserIntent.PROFILE_MANAGEMENT
    assert "Student Profile" in r5.response_text

    # Verify history maintains all 10 conversational turns (5 user + 5 assistant)
    history = orchestrator.get_session_history(session_id)
    assert len(history) == 10
