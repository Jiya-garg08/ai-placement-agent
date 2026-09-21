from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class Resume(Base, TimestampMixin):
    """Uploaded candidate resume with extracted and normalized entities."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    
    file_name = Column(String(255), nullable=False, default="resume.pdf")
    raw_text = Column(Text, nullable=False)
    redacted_text = Column(Text, nullable=False)
    
    # Structured entities extracted by Resume Agent (stored as JSON)
    extracted_skills = Column(JSON, default=list, nullable=False)
    extracted_education = Column(JSON, default=list, nullable=False)
    extracted_projects = Column(JSON, default=list, nullable=False)
    extracted_experience = Column(JSON, default=list, nullable=False)
    summary = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, profile_id={self.profile_id}, skills_count={len(self.extracted_skills)})>"


class JobDescription(Base, TimestampMixin):
    """Target job description associated with a student's preparation roadmap."""
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    company_name = Column(String(150), nullable=True)
    role_title = Column(String(150), nullable=False, default="Software Development Engineer (SDE)")
    experience_level = Column(String(100), nullable=True, default="Entry-Level / Fresher (0-1 yrs)")

    # Extracted requirements
    required_skills = Column(JSON, default=list, nullable=False)
    preferred_skills = Column(JSON, default=list, nullable=False)
    domain_keywords = Column(JSON, default=list, nullable=False)
    raw_text = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<JobDescription(id={self.id}, role_title='{self.role_title}', company='{self.company_name}')>"
