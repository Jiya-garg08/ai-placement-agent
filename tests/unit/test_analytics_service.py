import pytest
from database.database import init_db, SessionLocal
from database.models.student import User, StudentProfile
from database.models.assessment import Question, Assessment
from database.models.assessment_attempt import AssessmentAttempt, AssessmentAnswer
from database.models.practice import PracticeAttempt, PracticeStreak
from services.analytics_service import AnalyticsService, CORE_PLACEMENT_DOMAINS
from agents.evaluation_agent.evaluation_agent import PerformanceEvaluationAgent
from schemas.evaluation_schema import PlacementReadinessEvaluation


@pytest.fixture(autouse=True)
def setup_analytics_test_data():
    init_db()
    db = SessionLocal()

    # Create test candidate
    user = db.query(User).filter_by(email="analytics_eval@example.com").first()
    if not user:
        user = User(email="analytics_eval@example.com", name="Analytics Candidate")
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = StudentProfile(
            user_id=user.id,
            target_role="Software Development Engineer (SDE)",
            primary_skills=["Python", "DSA"]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    else:
        profile = user.profile

    # Create questions in DSA and DBMS
    q_dsa = db.query(Question).filter_by(topic="Data Structures & Algorithms").first()
    if not q_dsa:
        q_dsa = Question(
            topic="Data Structures & Algorithms",
            subtopic="Binary Search",
            question_text="Time complexity of binary search?",
            options=["O(1)", "O(log N)", "O(N)", "O(N^2)"],
            correct_option_index=1,
            explanation="Logarithmic time.",
            difficulty="Easy"
        )
        db.add(q_dsa)

    q_dbms = db.query(Question).filter_by(topic="Database Management Systems").first()
    if not q_dbms:
        q_dbms = Question(
            topic="Database Management Systems",
            subtopic="ACID",
            question_text="What does 'I' stand for in ACID?",
            options=["Integrity", "Isolation", "Index", "Iteration"],
            correct_option_index=1,
            explanation="Isolation ensures concurrent transactions execute independently.",
            difficulty="Easy"
        )
        db.add(q_dbms)

    db.commit()

    assessment = db.query(Assessment).first()
    if not assessment:
        assessment = Assessment(
            title="Diagnostic Placement Assessment",
            target_role="Software Development Engineer (SDE)",
            topic="Diagnostic Overall",
            difficulty="Intermediate",
            total_questions=2,
            time_limit_mins=20
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

    # Create assessment attempt and answers
    attempt = AssessmentAttempt(
        profile_id=profile.id,
        assessment_id=assessment.id,
        total_questions=2,
        total_correct=2,
        score_percentage=100.0,
        topic_scores=[
            {"topic": "Data Structures & Algorithms", "score": 100.0},
            {"topic": "Database Management Systems", "score": 100.0}
        ]
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    ans1 = AssessmentAnswer(
        attempt_id=attempt.id,
        question_id=q_dsa.id,
        selected_option_index=1,
        is_correct=True
    )
    ans2 = AssessmentAnswer(
        attempt_id=attempt.id,
        question_id=q_dbms.id,
        selected_option_index=1,
        is_correct=True
    )
    db.add_all([ans1, ans2])

    # Create practice attempt
    pa = PracticeAttempt(
        student_id=profile.id,
        question_id=q_dsa.id,
        topic="Data Structures & Algorithms",
        question_type="MCQ",
        user_answer="O(log N)",
        is_correct=True,
        time_spent_seconds=45,
        points_awarded=10
    )
    db.add(pa)

    # Create streak
    streak = db.query(PracticeStreak).filter_by(student_id=profile.id).first()
    if not streak:
        streak = PracticeStreak(
            student_id=profile.id,
            current_streak=3,
            longest_streak=5,
            total_questions_solved=10,
            total_correct=8
        )
        db.add(streak)

    db.commit()
    yield {"student_id": profile.id}
    db.close()


def test_topic_mastery_aggregation(setup_analytics_test_data):
    db = SessionLocal()
    service = AnalyticsService(session=db)
    student_id = setup_analytics_test_data["student_id"]

    masteries = service.get_topic_mastery_breakdown(student_id)
    assert len(masteries) == len(CORE_PLACEMENT_DOMAINS)

    dsa_item = next(m for m in masteries if m.topic == "Data Structures & Algorithms")
    assert dsa_item.assessments_taken == 1
    assert dsa_item.practice_problems_solved == 1
    assert dsa_item.accuracy_rate == 100.0
    assert dsa_item.level == "Mastered"

    dbms_item = next(m for m in masteries if m.topic == "Database Management Systems")
    assert dbms_item.assessments_taken == 1
    assert dbms_item.accuracy_rate == 100.0
    db.close()


def test_radar_chart_data_formatting(setup_analytics_test_data):
    db = SessionLocal()
    service = AnalyticsService(session=db)
    student_id = setup_analytics_test_data["student_id"]

    masteries = service.get_topic_mastery_breakdown(student_id)
    radar_data = service.get_radar_chart_data(masteries)

    assert "DSA" in radar_data
    assert "DBMS" in radar_data
    assert "OS" in radar_data
    assert radar_data["DSA"] == 100.0
    db.close()


def test_learning_velocity_calculation(setup_analytics_test_data):
    db = SessionLocal()
    service = AnalyticsService(session=db)
    student_id = setup_analytics_test_data["student_id"]

    velocity = service.calculate_learning_velocity(student_id)
    assert velocity.problems_per_day >= 0.0
    assert velocity.hours_per_week >= 0.0
    assert velocity.streak_days >= 1
    assert velocity.trend in ("Accelerating", "Consistent", "Decelerating")
    db.close()


def test_placement_readiness_index(setup_analytics_test_data):
    db = SessionLocal()
    service = AnalyticsService(session=db)
    student_id = setup_analytics_test_data["student_id"]

    masteries = service.get_topic_mastery_breakdown(student_id)
    readiness = service.compute_placement_readiness_index(masteries, "Software Development Engineer (SDE)")

    assert 0.0 <= readiness <= 100.0
    assert readiness > 50.0  # Since test attempts are 100% correct
    db.close()


def test_evaluation_agent_mock_mode(setup_analytics_test_data):
    db = SessionLocal()
    student_id = setup_analytics_test_data["student_id"]

    agent = PerformanceEvaluationAgent(mock_mode=True)
    evaluation = agent.evaluate_student(student_id, session=db)

    assert isinstance(evaluation, PlacementReadinessEvaluation)
    assert evaluation.student_id == student_id
    assert evaluation.readiness_tier in ("Interview Ready", "Competitive", "Early Stage", "Not Ready")
    assert len(evaluation.radar_chart_data) >= 8
    assert len(evaluation.strengths) >= 1
    assert "Data Structures" in evaluation.strengths[0]
    assert len(evaluation.recommended_focus_areas) >= 2
    assert "Candidate is currently evaluated" in evaluation.qualitative_evaluation_summary
    db.close()
