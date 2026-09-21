import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models.student import User, StudentProfile
from database.models.resume import Resume, JobDescription
from database.models.assessment_attempt import AssessmentAttempt
from database.models.skill_gap import SkillGap
from services.skill_gap_service import SkillGapService


@pytest.fixture
def db_session():
    """Create in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = User(email="gap.test@example.com", name="Gap Tester")
        session.add(user)
        session.commit()
        profile = StudentProfile(
            user_id=user.id,
            target_role="Software Development Engineer (SDE)",
            primary_skills=["Python", "SQL"]
        )
        session.add(profile)
        session.commit()
        yield session
    finally:
        session.close()


def test_deterministic_skill_gap_computation(db_session):
    service = SkillGapService(db_session)
    profile = db_session.query(StudentProfile).first()

    # 1. Resume has Python, SQL, Git
    resume = Resume(
        profile_id=profile.id,
        file_name="resume.pdf",
        raw_text="...",
        redacted_text="...",
        extracted_skills=["Python", "SQL", "Git"]
    )

    # 2. JD requires Python, SQL, Operating Systems, Computer Networks; prefers Docker
    jd = JobDescription(
        profile_id=profile.id,
        role_title="SDE",
        required_skills=["Python", "SQL", "Operating Systems", "Computer Networks"],
        preferred_skills=["Docker"],
        raw_text="..."
    )

    # 3. Assessment Attempt: Python 100%, Operating Systems 33%
    attempt = AssessmentAttempt(
        profile_id=profile.id,
        assessment_id=1,
        total_questions=5,
        total_correct=3,
        score_percentage=60.0,
        topic_scores=[
            {"topic": "Python", "correct": 2, "total": 2, "percentage": 100.0},
            {"topic": "Operating Systems", "correct": 1, "total": 3, "percentage": 33.33}
        ]
    )

    gap = service.analyze_and_persist_gaps(
        profile=profile,
        resume=resume,
        jd=jd,
        latest_attempt=attempt
    )

    assert gap.id is not None
    assert gap.profile_id == profile.id
    
    # Missing skills should be Computer Networks (and Operating Systems is in resume? No, it's weak)
    assert any("Computer Networks" in m for m in gap.missing_skills)
    
    # Weak skills should include Operating Systems (33.33%)
    assert any("Operating Systems" in w for w in gap.weak_skills)
    
    # Strong skills should include Python
    assert any("Python" in s for s in gap.strong_skills)

    # Priority topics should prioritize Operating Systems and Computer Networks
    p_topics = [p["topic"] for p in gap.priority_topics]
    assert "Operating Systems" in p_topics
    assert "Computer Networks" in p_topics

    # Overall readiness score should be within 0-100
    assert 40.0 <= gap.overall_readiness_score <= 90.0
