import pytest
from database.database import init_db, SessionLocal
from database.models.student import User, StudentProfile
from database.models.skill_gap import SkillGap
from database.models.practice import PracticeAttempt, PracticeStreak
from database.models.recommendation import NextBestAction
from services.next_action_service import NextActionService
from agents.recommendation_agent.recommendation_agent import NextActionRecommendationAgent
from schemas.recommendation_schema import NextActionRecommendationResponse


@pytest.fixture(autouse=True)
def setup_recommendation_test_data():
    init_db()
    db = SessionLocal()

    # Create test candidate
    user = db.query(User).filter_by(email="rec_candidate@example.com").first()
    if not user:
        user = User(email="rec_candidate@example.com", name="Recommendation Candidate")
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = StudentProfile(
            user_id=user.id,
            target_role="Software Development Engineer (SDE)",
            primary_skills=["Python"]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    else:
        profile = user.profile

    # Create a low-scoring practice attempt in SQL to create an empirical weak spot
    pa = PracticeAttempt(
        student_id=profile.id,
        topic="SQL",
        question_type="MCQ",
        user_answer="INCORRECT",
        is_correct=False,
        time_spent_seconds=40
    )
    db.add(pa)

    # Create a SkillGap with a missing skill
    gap = SkillGap(
        profile_id=profile.id,
        strong_skills=["Python"],
        weak_skills=["SQL (Accuracy: 0%)"],
        missing_skills=["Operating Systems"],
        priority_topics=[{"topic": "SQL", "urgency": "High"}],
        overall_readiness_score=35.0
    )
    db.add(gap)
    db.commit()

    yield {"student_id": profile.id}
    db.close()


def test_generate_next_actions_prioritizes_weak_spots(setup_recommendation_test_data):
    db = SessionLocal()
    student_id = setup_recommendation_test_data["student_id"]
    service = NextActionService(session=db)

    actions = service.generate_next_actions(student_id)

    assert len(actions) >= 1
    assert len(actions) <= 3

    # Primary action must target the empirical weak spot or missing skill
    first_action = actions[0]
    assert first_action.priority == "HIGH"
    assert first_action.target_page in ("Practice", "Tutor", "Assessments", "Roadmap")
    assert first_action.estimated_minutes >= 5
    assert first_action.id is not None  # Must be persisted

    # Check persistence in database
    persisted = db.query(NextBestAction).filter_by(student_id=student_id).all()
    assert len(persisted) == len(actions)
    db.close()


def test_mark_action_completed(setup_recommendation_test_data):
    db = SessionLocal()
    student_id = setup_recommendation_test_data["student_id"]
    service = NextActionService(session=db)

    actions = service.generate_next_actions(student_id)
    action_to_complete = actions[0]

    success = service.mark_action_completed(action_to_complete.id)
    assert success is True

    record = db.query(NextBestAction).filter_by(id=action_to_complete.id).first()
    assert record.is_completed is True
    assert record.completed_at is not None
    db.close()


def test_get_saved_actions(setup_recommendation_test_data):
    db = SessionLocal()
    student_id = setup_recommendation_test_data["student_id"]
    service = NextActionService(session=db)

    service.generate_next_actions(student_id)
    saved = service.get_saved_actions(student_id)

    assert len(saved) >= 1
    assert all(s.student_id == student_id for s in saved)
    db.close()


def test_recommendation_agent_mock_advice(setup_recommendation_test_data):
    db = SessionLocal()
    student_id = setup_recommendation_test_data["student_id"]

    service = NextActionService(session=db)
    agent = NextActionRecommendationAgent(action_service=service, mock_mode=True)

    resp = agent.get_recommendations(student_id)

    assert isinstance(resp, NextActionRecommendationResponse)
    assert resp.student_id == student_id
    assert len(resp.actions) >= 1
    assert "Today's Strategic Focus" in resp.motivational_summary
    assert resp.primary_weakness is not None
    db.close()
