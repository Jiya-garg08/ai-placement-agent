from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from database.database import Base, TimestampMixin


class SkillGap(Base, TimestampMixin):
    """Triangulated skill gap analysis between student profile, resume, target JD, and test scores."""
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    strong_skills = Column(JSON, default=list, nullable=False)
    weak_skills = Column(JSON, default=list, nullable=False)
    missing_skills = Column(JSON, default=list, nullable=False)
    priority_topics = Column(JSON, default=list, nullable=False)
    
    overall_readiness_score = Column(Float, nullable=False, default=50.0)

    def __repr__(self) -> str:
        return f"<SkillGap(id={self.id}, profile_id={self.profile_id}, readiness={self.overall_readiness_score}%)>"
