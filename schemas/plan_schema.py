from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LearningPlanItemSchema(BaseModel):
    id: Optional[int] = None
    week_number: int = Field(..., ge=1, le=12)
    order_index: int = Field(..., ge=1)
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    priority: str = Field(default="Medium", description="High, Medium, or Low")
    learning_objectives: str
    practice_goal_count: int = Field(default=10, ge=1)
    status: str = Field(default="Pending", description="Pending, In Progress, or Completed")

    model_config = ConfigDict(from_attributes=True)


class LearningPlanStructure(BaseModel):
    """Structured output schema expected from Learning Planner Agent."""
    plan_name: str = Field(default="4-Week Placement Readiness Roadmap")
    target_role: str
    total_weeks: int = Field(default=4, ge=1, le=12)
    daily_hours_target: float = Field(default=2.5, ge=1.0, le=8.0)
    items: List[LearningPlanItemSchema] = Field(default_factory=list)


class LearningPlanResponse(BaseModel):
    id: int
    profile_id: int
    plan_name: str
    target_role: str
    total_weeks: int
    daily_hours_target: float
    is_active: bool
    items: List[LearningPlanItemSchema] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
