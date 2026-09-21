import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from database.database import Base
from database.models.student import User, StudentProfile
from services.student_service import StudentService
from schemas.profile_schema import StudentOnboardingRequest, StudentProfileUpdate


@pytest.fixture
def session():
    """Create an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    s = Session()
    try:
        yield s
    finally:
        s.close()


def test_student_onboarding_success(session):
    service = StudentService(session)
    request = StudentOnboardingRequest(
        name="Alex Mercer",
        email="alex.mercer@example.com",
        target_role="Software Development Engineer (SDE)",
        career_goal="FAANG SDE-1",
        target_company_tier="Tier 1 / Product",
        college="Stanford University",
        graduation_year=2026,
        current_semester=7,
        primary_skills=["Python", "Data Structures", "SQL"]
    )
    user, profile = service.onboard_student(request)
    
    assert user.id is not None
    assert user.email == "alex.mercer@example.com"
    assert user.name == "Alex Mercer"
    assert profile.user_id == user.id
    assert profile.target_role == "Software Development Engineer (SDE)"
    assert "Python" in profile.primary_skills
    assert profile.graduation_year == 2026


def test_student_re_onboarding_updates_profile(session):
    service = StudentService(session)
    request1 = StudentOnboardingRequest(
        name="Samantha Reed",
        email="samantha@example.com",
        target_role="Frontend Engineer",
        primary_skills=["JavaScript", "React"]
    )
    user1, profile1 = service.onboard_student(request1)
    
    request2 = StudentOnboardingRequest(
        name="Samantha Reed",
        email="samantha@example.com",
        target_role="Full Stack Engineer",
        primary_skills=["JavaScript", "React", "Node.js", "SQL"]
    )
    user2, profile2 = service.onboard_student(request2)

    assert user1.id == user2.id
    assert profile1.id == profile2.id
    assert profile2.target_role == "Full Stack Engineer"
    assert len(profile2.primary_skills) == 4


def test_student_update_profile(session):
    service = StudentService(session)
    request = StudentOnboardingRequest(
        name="Jordan Lee",
        email="jordan@example.com",
        target_role="Data Engineer"
    )
    user, _ = service.onboard_student(request)

    updated = service.update_profile(
        user.id,
        StudentProfileUpdate(career_goal="Top Fintech Data Engineer", graduation_year=2027)
    )
    assert updated is not None
    assert updated.career_goal == "Top Fintech Data Engineer"
    assert updated.graduation_year == 2027


def test_invalid_email_validation():
    with pytest.raises(ValidationError):
        StudentOnboardingRequest(
            name="Test User",
            email="not-an-email",
            target_role="SDE"
        )
