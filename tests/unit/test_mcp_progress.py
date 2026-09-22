import pytest
from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from database.models.assessment_attempt import AssessmentAttempt
from database.models.learning_plan import LearningPlan, LearningPlanItem
from mcp_service.tools.progress_tool import (
    get_student_performance_summary,
    get_active_learning_roadmap,
    mark_roadmap_item_status
)


@pytest.fixture
def test_setup():
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "progress.test@example.com").first()
        if not user:
            user = User(email="progress.test@example.com", name="Progress Tester")
            db.add(user)
            db.commit()
            profile = StudentProfile(user_id=user.id, target_role="SDE")
            db.add(profile)
            db.commit()

            # Add an attempt
            attempt = AssessmentAttempt(
                profile_id=profile.id,
                assessment_id=1,
                total_questions=10,
                total_correct=7,
                score_percentage=70.0,
                topic_scores=[
                    {"topic": "Data Structures & Algorithms", "correct": 4, "total": 5, "percentage": 80.0},
                    {"topic": "Operating Systems", "correct": 1, "total": 3, "percentage": 33.33}
                ]
            )
            db.add(attempt)

            # Add an active plan with items
            plan = LearningPlan(
                profile_id=profile.id,
                plan_name="Test Roadmap",
                target_role="SDE",
                total_weeks=4,
                is_active=True
            )
            db.add(plan)
            db.flush()

            item1 = LearningPlanItem(
                plan_id=plan.id,
                week_number=1,
                order_index=1,
                topic="Operating Systems Remediation",
                priority="High",
                learning_objectives="Fix deadlock concept deficiencies",
                status="In Progress"
            )
            item2 = LearningPlanItem(
                plan_id=plan.id,
                week_number=2,
                order_index=2,
                topic="Dynamic Programming Masterclass",
                priority="High",
                learning_objectives="Learn tabulation and memoization",
                status="Pending"
            )
            db.add_all([item1, item2])
            db.commit()
            db.refresh(user)

        return user
    finally:
        db.close()


def test_mcp_get_student_performance_summary(test_setup):
    summary = get_student_performance_summary(test_setup.id)
    assert summary["status"] == "success"
    assert summary["total_quizzes_completed"] >= 1
    assert summary["overall_accuracy_percentage"] >= 60.0
    assert any("Operating Systems" in w for w in summary["weakest_topics"])
    assert any("Data Structures" in s for s in summary["strongest_topics"])


def test_mcp_get_active_learning_roadmap(test_setup):
    roadmap = get_active_learning_roadmap(test_setup.id)
    assert roadmap["status"] == "success"
    assert roadmap["has_active_plan"] is True
    assert len(roadmap["items"]) >= 2
    assert roadmap["items"][0]["topic"] == "Operating Systems Remediation"


def test_mcp_mark_roadmap_item_status(test_setup):
    roadmap = get_active_learning_roadmap(test_setup.id)
    item_id = roadmap["items"][0]["id"]

    res = mark_roadmap_item_status(item_id, "Completed")
    assert res["status"] == "success"
    assert res["new_status"] == "Completed"

    # Verify updated
    updated_roadmap = get_active_learning_roadmap(test_setup.id)
    assert updated_roadmap["items"][0]["status"] == "Completed"
    assert updated_roadmap["progress_percentage"] > 0.0


def test_mcp_mark_roadmap_item_invalid_status():
    res = mark_roadmap_item_status(1, "InvalidStatus")
    assert res["status"] == "error"
    assert "Invalid status" in res["message"]
