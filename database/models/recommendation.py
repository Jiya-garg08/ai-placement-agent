from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class NextBestAction(Base, TimestampMixin):
    """Urgent tactical next best action recommended for a candidate to accelerate interview readiness."""
    __tablename__ = "next_best_actions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    action_type = Column(String(50), nullable=False)  # 'PRACTICE_DRILL', 'DIAGNOSTIC_TEST', 'TUTOR_REVIEW', 'ROADMAP_MILESTONE'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    topic = Column(String(100), nullable=False, index=True)
    priority = Column(String(20), nullable=False, default="HIGH")  # 'HIGH', 'MEDIUM', 'LOW'
    estimated_minutes = Column(Integer, nullable=False, default=15)
    target_page = Column(String(50), nullable=False)  # 'Practice', 'Tutor', 'Assessments', 'Roadmap'
    
    # Context payload passed into target UI page
    action_payload = Column(JSON, default=dict, nullable=False)

    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("StudentProfile")

    def __repr__(self) -> str:
        return f"<NextBestAction(id={self.id}, student_id={self.student_id}, title='{self.title}', priority='{self.priority}')>"
