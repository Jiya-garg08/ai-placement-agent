from datetime import date, timedelta
import pytest
from database.database import init_db, SessionLocal
from database.models.student import User, StudentProfile
from database.models.assessment import Question
from database.models.practice import PracticeAttempt, PracticeStreak
from schemas.practice_schema import PracticeSubmissionRequest
from services.practice_service import PracticeService


@pytest.fixture(autouse=True)
def setup_practice_test_data():
    init_db()
    db = SessionLocal()

    # Setup student
    user = db.query(User).filter_by(email="practice_test@example.com").first()
    if not user:
        user = User(email="practice_test@example.com", name="Practice Student")
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

    # Setup seed practice questions if none exist
    q = db.query(Question).filter_by(topic="Data Structures & Algorithms").first()
    if not q:
        q = Question(
            topic="Data Structures & Algorithms",
            subtopic="Binary Search",
            question_text="What is the worst-case time complexity of binary search on a sorted array of size N?",
            options=["O(1)", "O(log N)", "O(N)", "O(N log N)"],
            correct_option_index=1,
            explanation="Binary search repeatedly halves the search space, resulting in logarithmic O(log N) time complexity.",
            difficulty="Easy"
        )
        db.add(q)
        db.commit()
        db.refresh(q)

    yield {"student_id": profile.id, "question_id": q.id}
    db.close()


def test_get_practice_questions(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)

    questions = service.get_practice_questions(topic="Data Structures", limit=5)
    assert len(questions) >= 1
    assert any("Binary Search" in q.subtopic for q in questions if q.subtopic)
    assert len(questions[0].options) == 4
    db.close()


def test_get_coding_snippets():
    service = PracticeService()
    snippets = service.get_coding_snippets()
    assert len(snippets) >= 3

    dsa_snippets = service.get_coding_snippets(topic="Algorithms")
    assert len(dsa_snippets) >= 1
    assert any(s.id == "dsa-01-two-sum" for s in dsa_snippets)


def test_submit_correct_mcq_practice(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)
    student_id = setup_practice_test_data["student_id"]
    question_id = setup_practice_test_data["question_id"]
    q = db.query(Question).filter_by(id=question_id).first()

    sub = PracticeSubmissionRequest(
        student_id=student_id,
        question_id=question_id,
        selected_option_index=q.correct_option_index,
        time_spent_seconds=25
    )

    resp = service.submit_practice_attempt(sub)

    assert resp.is_correct is True
    assert resp.points_awarded == 10
    assert resp.current_streak >= 1
    assert "Excellent" in resp.feedback
    db.close()


def test_submit_incorrect_mcq_practice(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)
    student_id = setup_practice_test_data["student_id"]
    question_id = setup_practice_test_data["question_id"]
    q = db.query(Question).filter_by(id=question_id).first()

    sub = PracticeSubmissionRequest(
        student_id=student_id,
        question_id=question_id,
        selected_option_index=(q.correct_option_index + 1) % len(q.options),
        time_spent_seconds=15
    )

    resp = service.submit_practice_attempt(sub)

    assert resp.is_correct is False
    assert resp.points_awarded == 2  # Effort points
    assert resp.correct_option_index == q.correct_option_index
    assert "Keep going" in resp.feedback
    db.close()


def test_streak_progression_and_reset(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)
    student_id = setup_practice_test_data["student_id"]
    question_id = setup_practice_test_data["question_id"]

    # Clear previous streak
    db.query(PracticeStreak).filter_by(student_id=student_id).delete()
    db.commit()

    # 1. Day 1: First solve
    sub1 = PracticeSubmissionRequest(student_id=student_id, question_id=question_id, selected_option_index=1)
    r1 = service.submit_practice_attempt(sub1)
    assert r1.current_streak == 1

    # 2. Simulate next consecutive day (yesterday was day 1)
    streak_record = db.query(PracticeStreak).filter_by(student_id=student_id).first()
    streak_record.last_practice_date = date.today() - timedelta(days=1)
    db.commit()

    sub2 = PracticeSubmissionRequest(student_id=student_id, question_id=question_id, selected_option_index=1)
    r2 = service.submit_practice_attempt(sub2)
    assert r2.current_streak == 2

    # 3. Simulate broken streak (last practice was 3 days ago)
    streak_record = db.query(PracticeStreak).filter_by(student_id=student_id).first()
    streak_record.last_practice_date = date.today() - timedelta(days=3)
    db.commit()

    sub3 = PracticeSubmissionRequest(student_id=student_id, question_id=question_id, selected_option_index=1)
    r3 = service.submit_practice_attempt(sub3)
    assert r3.current_streak == 1  # Reset to 1

    # But longest streak remains 2
    streak_record = db.query(PracticeStreak).filter_by(student_id=student_id).first()
    assert streak_record.longest_streak == 2
    db.close()


def test_submit_coding_snippet(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)
    student_id = setup_practice_test_data["student_id"]

    sub = PracticeSubmissionRequest(
        student_id=student_id,
        snippet_id="dsa-01-two-sum",
        code_submission="""def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []"""
    )

    resp = service.submit_practice_attempt(sub)
    assert resp.is_correct is True
    assert resp.points_awarded == 10
    assert "Complexity Profile" in resp.explanation
    db.close()


def test_get_student_practice_summary(setup_practice_test_data):
    db = SessionLocal()
    service = PracticeService(session=db)
    student_id = setup_practice_test_data["student_id"]

    summary = service.get_student_practice_summary(student_id)
    assert summary.student_id == student_id
    assert summary.total_questions_solved >= 1
    assert 0.0 <= summary.overall_accuracy <= 100.0
    assert isinstance(summary.topic_breakdown, dict)
    db.close()
