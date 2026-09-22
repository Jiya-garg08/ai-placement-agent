from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class TopicMasteryItem(BaseModel):
    """Detailed topic competency metrics and mastery level."""
    topic: str
    mastery_percentage: float = Field(..., ge=0.0, le=100.0)
    level: str = Field(..., description="'Novice', 'Developing', 'Competent', or 'Mastered'")
    assessments_taken: int = Field(default=0, ge=0)
    practice_problems_solved: int = Field(default=0, ge=0)
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=100.0)

    model_config = ConfigDict(from_attributes=True)


class LearningVelocity(BaseModel):
    """Student preparation speed, daily consistency, and momentum trajectory."""
    problems_per_day: float = Field(default=0.0, ge=0.0)
    hours_per_week: float = Field(default=0.0, ge=0.0)
    trend: str = Field(default="Consistent", description="'Accelerating', 'Consistent', or 'Decelerating'")
    streak_days: int = Field(default=0, ge=0)


class PlacementReadinessEvaluation(BaseModel):
    """Holistic placement evaluation combining quantitative mastery scores and qualitative AI appraisal."""
    student_id: int
    target_role: str
    overall_readiness_index: float = Field(..., ge=0.0, le=100.0)
    readiness_tier: str = Field(..., description="'Not Ready', 'Early Stage', 'Competitive', or 'Interview Ready'")
    topic_masteries: List[TopicMasteryItem] = Field(default_factory=list)
    radar_chart_data: Dict[str, float] = Field(
        default_factory=dict,
        description="Normalized topic scores (0-100) formatted for Plotly/Streamlit radar chart"
    )
    learning_velocity: LearningVelocity
    strengths: List[str] = Field(default_factory=list)
    critical_gaps: List[str] = Field(default_factory=list)
    qualitative_evaluation_summary: str
    recommended_focus_areas: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
