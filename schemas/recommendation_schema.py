from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ActionItem(BaseModel):
    """Specific tactical action recommended to candidate with direct target destination."""
    id: Optional[int] = None
    action_type: str = Field(..., description="'PRACTICE_DRILL', 'DIAGNOSTIC_TEST', 'TUTOR_REVIEW', 'ROADMAP_MILESTONE'")
    title: str
    description: str
    topic: str
    priority: str = Field(default="HIGH", description="'HIGH', 'MEDIUM', or 'LOW'")
    estimated_minutes: int = Field(default=15, ge=5, le=120)
    target_page: str = Field(..., description="'Practice', 'Tutor', 'Assessments', or 'Roadmap'")
    action_payload: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class NextActionRecommendationResponse(BaseModel):
    """Set of 1-3 urgent tactical actions surfaced to maximize daily preparation impact."""
    student_id: int
    overall_readiness_index: float = Field(default=0.0, ge=0.0, le=100.0)
    primary_weakness: Optional[str] = None
    actions: List[ActionItem] = Field(default_factory=list)
    motivational_summary: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
