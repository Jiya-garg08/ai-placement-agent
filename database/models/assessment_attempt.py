from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class AssessmentAttempt(Base, TimestampMixin):
    """Historical record of a completed diagnostic or topic-level quiz attempt."""
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), index=True, nullable=False)

    total_questions = Column(Integer, nullable=False)
    total_correct = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    
    # Topic level percentage breakdown stored as structured JSON
    topic_scores = Column(JSON, default=list, nullable=False)

    # Relationships
    answers = relationship("AssessmentAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AssessmentAttempt(id={self.id}, profile_id={self.profile_id}, score={self.score_percentage}%)>"


class AssessmentAnswer(Base, TimestampMixin):
    """Specific option selected by candidate for a single question in an attempt."""
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)

    selected_option_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    attempt = relationship("AssessmentAttempt", back_populates="answers")

    def __repr__(self) -> str:
        return f"<AssessmentAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"
