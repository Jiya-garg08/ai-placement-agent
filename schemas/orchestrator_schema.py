from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from schemas.rag_schema import CitationSource


class UserIntent(str, Enum):
    """Classified student intents within the placement preparation agent."""
    RESUME_ANALYSIS = "resume_analysis"
    DIAGNOSTIC_ASSESSMENT = "diagnostic_assessment"
    SKILL_GAP_ANALYSIS = "skill_gap_analysis"
    ROADMAP_PLANNING = "roadmap_planning"
    RAG_TUTOR = "rag_tutor"
    PROFILE_MANAGEMENT = "profile_management"
    PORTFOLIO_INSPECTION = "portfolio_inspection"
    PRACTICE_DRILL = "practice_drill"
    NEXT_BEST_ACTION = "next_best_action"
    GENERAL_CONVERSATION = "general_conversation"


class IntentClassificationResult(BaseModel):
    """Result of classifying a student prompt into an actionable intent with parameters."""
    intent: UserIntent
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    extracted_params: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None


class ChatMessage(BaseModel):
    """Individual conversational turn in an orchestrator session."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    intent: Optional[UserIntent] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ConversationSession(BaseModel):
    """Multi-turn conversation session maintaining candidate interaction state."""
    session_id: str
    student_id: Optional[int] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrchestratorResponse(BaseModel):
    """Standardized response from the Foundry Master Orchestrator."""
    session_id: str
    intent: UserIntent
    delegated_agent: str
    response_text: str
    citations: List[CitationSource] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
