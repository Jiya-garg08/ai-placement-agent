import json
from typing import Optional, List, Dict, Any

from config.settings import settings
from database.database import SessionLocal
from database.models.student import StudentProfile
from schemas.recommendation_schema import (
    NextActionRecommendationResponse,
    ActionItem
)
from services.next_action_service import NextActionService
from services.analytics_service import AnalyticsService

COACH_SYSTEM_PROMPT = """You are an elite Placement Mentor and Strategic Coach.
Your goal is to inspect a candidate's tactical recommended actions and synthesize an inspiring, high-impact motivational summary that focuses their daily study session on empirical weak spots.
Be concise, direct, and action-oriented.
"""


class NextActionRecommendationAgent:
    """Agent that formulates contextual advice and high-impact daily priorities for candidate placement prep."""

    def __init__(
        self,
        action_service: Optional[NextActionService] = None,
        mock_mode: Optional[bool] = None
    ):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.action_service = action_service or NextActionService()

    def get_recommendations(self, student_id: int) -> NextActionRecommendationResponse:
        """Produce 1-3 targeted tactical actions and cohesive motivational coaching advice."""
        actions = self.action_service.generate_next_actions(student_id)

        # Retrieve student readiness
        analytics = AnalyticsService(session=self.action_service.session)
        masteries = analytics.get_topic_mastery_breakdown(student_id)
        profile = self.action_service.session.query(StudentProfile).filter_by(id=student_id).first()
        target_role = profile.target_role if profile else "Software Development Engineer (SDE)"
        readiness_score = analytics.compute_placement_readiness_index(masteries, target_role)

        primary_weakness = actions[0].topic if actions else "Foundational Problem Solving"

        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            summary = self._heuristic_mock_advice(target_role, readiness_score, actions)
        else:
            try:
                summary = self._llm_advice(target_role, readiness_score, actions)
            except Exception:
                summary = self._heuristic_mock_advice(target_role, readiness_score, actions)

        return NextActionRecommendationResponse(
            student_id=student_id,
            overall_readiness_index=readiness_score,
            primary_weakness=primary_weakness,
            actions=actions,
            motivational_summary=summary
        )

    def _heuristic_mock_advice(
        self,
        target_role: str,
        readiness_score: float,
        actions: List[ActionItem]
    ) -> str:
        """Synthesize action-oriented coach advice deterministically with zero Azure token cost."""
        if not actions:
            return f"Keep up the disciplined study routine for your target role: {target_role}."

        top_action = actions[0]
        advice_lines = [
            f"🎯 **Today's Strategic Focus for {target_role}** (Readiness: {readiness_score:.1f}%):",
            f"Your primary lever today is **{top_action.title}** ({top_action.estimated_minutes} mins).",
            f"{top_action.reasoning}",
            f"Once completed, navigate directly to **{top_action.target_page}** to lock in your daily streak!"
        ]
        return "\n".join(advice_lines)

    def _llm_advice(
        self,
        target_role: str,
        readiness_score: float,
        actions: List[ActionItem]
    ) -> str:
        """Call Azure OpenAI / Foundry model for contextual coaching advice."""
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        prompt_payload = {
            "target_role": target_role,
            "readiness_score": readiness_score,
            "top_actions": [a.model_dump() for a in actions]
        }

        resp = client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": COACH_SYSTEM_PROMPT},
                {"role": "user", "content": f"Synthesize concise daily coaching advice for:\n{json.dumps(prompt_payload, indent=2)}"}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return resp.choices[0].message.content or "Focus on completing your top recommended action today."
