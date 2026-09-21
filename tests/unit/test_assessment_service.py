import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models.assessment import Assessment, Question
from scripts.seed_data import seed_questions
from services.assessment_service import AssessmentService
from schemas.assessment_schema import AssessmentSubmission, AssessmentAnswerSubmission


@pytest.fixture
def db_session():
    """Create in-memory SQLite database populated with seeded questions."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        seed_questions(session)
        yield session
    finally:
        session.close()


def test_seed_questions_count(db_session):
    count = db_session.query(Question).count()
    assert count >= 15


def test_create_diagnostic_assessment(db_session):
    service = AssessmentService(db_session)
    assessment = service.create_diagnostic_assessment(
        target_role="Software Development Engineer (SDE)",
        total_questions=10
    )
    assert assessment.id is not None
    assert assessment.total_questions == 10
    assert len(assessment.questions) == 10
    
    # Check that questions belong to multiple core domains
    topics = set(q.topic for q in assessment.questions)
    assert len(topics) >= 3


def test_evaluate_assessment_submission(db_session):
    service = AssessmentService(db_session)
    assessment = service.create_diagnostic_assessment("Backend Engineer", total_questions=5)
    
    # Simulate user answering: answer first 3 questions correctly, rest incorrectly
    answers = []
    for idx, q in enumerate(assessment.questions):
        selected_opt = q.correct_option_index if idx < 3 else (q.correct_option_index + 1) % 4
        answers.append(AssessmentAnswerSubmission(
            question_id=q.id,
            selected_option_index=selected_opt
        ))

    submission = AssessmentSubmission(
        assessment_id=assessment.id,
        profile_id=1,
        answers=answers
    )

    result = service.evaluate_submission(submission)
    assert result.total_questions == 5
    assert result.total_correct == 3
    assert result.score_percentage == 60.0
    assert len(result.topic_breakdown) >= 1
