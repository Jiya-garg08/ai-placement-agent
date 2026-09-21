import io
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models.student import User, StudentProfile
from database.models.resume import Resume, JobDescription
from database.repositories.resume_repository import ResumeRepository, JobDescriptionRepository
from services.resume_service import ResumeService
from agents.resume_agent.resume_agent import ResumeAnalysisAgent
from schemas.resume_schema import ExtractedResume

SAMPLE_TEXT = """
Jane Doe
Summary: Aspiring Full Stack SDE with a passion for high-concurrency systems.

Education
Carnegie Mellon University - B.S. in Computer Science (2022 - 2026)
GPA: 3.95/4.0

Technical Skills
Python, Java, C++, SQL, PostgreSQL, Docker, Operating Systems, Algorithms

Work Experience
Software Engineering Intern at Google (Summer 2025)
- Optimized distributed database queries.

Projects
Distributed Cache Engine
- Built an in-memory key-value store in Python.
"""


@pytest.fixture
def db_session():
    """Create in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_resume_analysis_agent_mock_mode():
    stream = io.BytesIO(SAMPLE_TEXT.encode("utf-8"))
    parsed = ResumeService.parse_resume(stream, "jane_doe.txt")
    
    agent = ResumeAnalysisAgent(mock_mode=True)
    extracted = agent.analyze(parsed)

    assert isinstance(extracted, ExtractedResume)
    assert "Jane Doe" in extracted.candidate_name
    assert len(extracted.skills) >= 5
    assert "Python" in extracted.skills
    assert "Postgresql" in extracted.skills
    assert len(extracted.education) >= 1
    assert extracted.education[0].graduation_year == 2026
    assert len(extracted.experience) >= 1
    assert "Google" in extracted.experience[0].company


def test_resume_and_jd_database_persistence(db_session):
    # 1. Create student
    user = User(email="jane@example.com", name="Jane Doe")
    db_session.add(user)
    db_session.commit()

    profile = StudentProfile(user_id=user.id, target_role="SDE")
    db_session.add(profile)
    db_session.commit()

    resume_repo = ResumeRepository(db_session)
    jd_repo = JobDescriptionRepository(db_session)

    # 2. Persist resume
    resume = Resume(
        profile_id=profile.id,
        file_name="jane_doe.pdf",
        raw_text=SAMPLE_TEXT,
        redacted_text=SAMPLE_TEXT,
        extracted_skills=["Python", "SQL", "Docker"],
        extracted_education=[{"degree": "BS", "grad_year": 2026}],
        extracted_projects=[{"title": "Cache Engine"}],
        extracted_experience=[{"company": "Google"}],
        summary="Aspiring Full Stack SDE"
    )
    saved_resume = resume_repo.create(resume)
    assert saved_resume.id is not None
    assert len(saved_resume.extracted_skills) == 3

    # 3. Persist Job Description
    jd = JobDescription(
        profile_id=profile.id,
        company_name="Google",
        role_title="Software Engineer 1",
        required_skills=["Python", "Algorithms", "SQL"],
        preferred_skills=["Docker", "Kubernetes"],
        domain_keywords=["Distributed Systems"],
        raw_text="Job description text..."
    )
    saved_jd = jd_repo.create(jd)
    assert saved_jd.id is not None
    assert saved_jd.company_name == "Google"

    # 4. Query by profile ID
    latest_resume = resume_repo.get_latest_for_profile(profile.id)
    assert latest_resume is not None
    assert latest_resume.file_name == "jane_doe.pdf"

    latest_jd = jd_repo.get_latest_for_profile(profile.id)
    assert latest_jd is not None
    assert latest_jd.role_title == "Software Engineer 1"
