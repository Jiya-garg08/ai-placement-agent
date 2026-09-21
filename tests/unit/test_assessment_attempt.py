import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models.student import User, StudentProfile
from database.models.assessment import Assessment, Question
from database.models.assessment_attempt import AssessmentAttempt
from database.repositories.attempt_repository import AssessmentAttemptRepository
from scripts.seed_data import seed_questions
from services.assessment_service import AssessmentService
from schemas.assessment_schema import AssessmentSubmission, AssessmentAnswerSubmission


@pytest.fixture
def db_session():
    """Create in-memory SQLite database populated with student and questions."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        seed_questions(session)
        user = User(email="test.student@example.com", name="Test Student")
        session.add(user)
        session.commit()
        profile = StudentProfile(user_id=user.id, target_role="Software Development Engineer (SDE)")
        session.add(profile)
        session.commit()
        yield session
    finally:
        session.close()


def test_record_submission_persists_attempt_and_answers(db_session):
    service = AssessmentService(db_session)
    assessment = service.create_diagnostic_assessment("Software Development Engineer (SDE)", total_questions=5)
    
    # 4 correct, 1 incorrect
    answers = []
    for idx, q in enumerate(assessment.questions):
        opt = q.correct_option_index if idx < 4 else (q.correct_option_index + 1) % 4
        answers.append(AssessmentAnswerSubmission(question_id=q.id, selected_option_index=opt))

    submission = AssessmentSubmission(
        assessment_id=assessment.id,
        profile_id=1,
        answers=answers
    )

    attempt = service.record_submission(submission)

    assert attempt.id is not None
    assert attempt.profile_id == 1
    assert attempt.total_questions == 5
    assert attempt.total_correct == 4
    assert attempt.score_percentage == 80.0
    assert len(attempt.answers) == 5
    assert len(attempt.topic_scores) >= 1

    # Verify querying through repository
    repo = AssessmentAttemptRepository(db_session)
    latest = repo.get_latest_attempt(profile_id=1)
    assert latest is not None
    assert latest.id == attempt.id

    mastery = repo.get_aggregated_topic_mastery(profile_id=1)
    assert isinstance(mastery, dict)
    assert len(mastery) >= 1
