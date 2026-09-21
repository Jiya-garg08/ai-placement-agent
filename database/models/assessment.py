from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    """Calibrated diagnostic assessment entity for evaluating placement readiness."""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    target_role = Column(String(150), nullable=False, default="Software Development Engineer (SDE)")
    topic = Column(String(100), nullable=False, default="Diagnostic Overall")
    difficulty = Column(String(50), nullable=False, default="Intermediate")
    total_questions = Column(Integer, nullable=False, default=10)
    time_limit_mins = Column(Integer, nullable=False, default=20)

    # Relationships
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, title='{self.title}', questions={self.total_questions})>"


class Question(Base, TimestampMixin):
    """Individual assessment or practice question with options and objective answer key."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True)

    topic = Column(String(100), nullable=False, index=True)
    subtopic = Column(String(100), nullable=True)
    question_text = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True)
    
    # 4 distinct choices as JSON array of strings
    options = Column(JSON, nullable=False)
    # Zero-indexed correct choice (0, 1, 2, or 3)
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False, default="Medium")

    # Relationship back to assessment
    assessment = relationship("Assessment", back_populates="questions")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, topic='{self.topic}', difficulty='{self.difficulty}')>"
