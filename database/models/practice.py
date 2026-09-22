from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class PracticeAttempt(Base, TimestampMixin):
    """Log of a student's individual practice question attempt, telemetry, and feedback."""
    __tablename__ = "practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True, index=True)

    topic = Column(String(100), nullable=False, index=True)
    subtopic = Column(String(100), nullable=True)
    question_type = Column(String(50), nullable=False, default="MCQ")  # 'MCQ', 'CODE_SNIPPET', 'SQL_QUERY'
    user_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    feedback = Column(Text, nullable=True)
    points_awarded = Column(Integer, nullable=False, default=0)

    # Relationships
    student = relationship("StudentProfile")
    question = relationship("Question")

    def __repr__(self) -> str:
        return f"<PracticeAttempt(id={self.id}, student_id={self.student_id}, topic='{self.topic}', is_correct={self.is_correct})>"


class PracticeStreak(Base, TimestampMixin):
    """Cumulative telemetry tracking consecutive practice days and aggregate problem solving stats."""
    __tablename__ = "practice_streaks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_practice_date = Column(Date, nullable=True)
    total_questions_solved = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)

    # Relationships
    student = relationship("StudentProfile")

    def __repr__(self) -> str:
        return f"<PracticeStreak(student_id={self.student_id}, streak={self.current_streak}, solved={self.total_questions_solved})>"
