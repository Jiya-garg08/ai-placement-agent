from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PriorityTopicItem(BaseModel):
    topic: str
    urgency: str = Field(..., description="High, Medium, or Low")
    rationale: str


class SkillGapReport(BaseModel):
    id: Optional[int] = None
    profile_id: int
    strong_skills: List[str] = Field(default_factory=list)
    weak_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    priority_topics: List[PriorityTopicItem] = Field(default_factory=list)
    overall_readiness_score: float = Field(default=50.0, ge=0.0, le=100.0)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
