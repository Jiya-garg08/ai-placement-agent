from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base, TimestampMixin


class LearningPlan(Base, TimestampMixin):
    """Personalized adaptive learning roadmap generated for a student."""
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    plan_name = Column(String(200), nullable=False, default="4-Week Placement Readiness Roadmap")
    target_role = Column(String(150), nullable=False)
    total_weeks = Column(Integer, nullable=False, default=4)
    daily_hours_target = Column(Float, nullable=False, default=2.5)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    items = relationship("LearningPlanItem", back_populates="plan", cascade="all, delete-orphan", order_by="LearningPlanItem.order_index")

    def __repr__(self) -> str:
        return f"<LearningPlan(id={self.id}, profile_id={self.profile_id}, weeks={self.total_weeks})>"


class LearningPlanItem(Base, TimestampMixin):
    """Individual topic milestone within a learning plan."""
    __tablename__ = "learning_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id", ondelete="CASCADE"), index=True, nullable=False)

    week_number = Column(Integer, nullable=False)
    order_index = Column(Integer, nullable=False)
    topic = Column(String(150), nullable=False)
    subtopics = Column(JSON, default=list, nullable=False)
    priority = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    learning_objectives = Column(Text, nullable=False)
    practice_goal_count = Column(Integer, nullable=False, default=10)
    status = Column(String(50), nullable=False, default="Pending")  # Pending, In Progress, Completed

    plan = relationship("LearningPlan", back_populates="items")

    def __repr__(self) -> str:
        return f"<LearningPlanItem(id={self.id}, topic='{self.topic}', week={self.week_number}, status='{self.status}')>"
