import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from config.settings import settings
from database.database import SessionLocal
from database.models.student import StudentProfile
from schemas.evaluation_schema import (
    PlacementReadinessEvaluation,
    TopicMasteryItem,
    LearningVelocity
)
from services.analytics_service import AnalyticsService

EVALUATION_SYSTEM_PROMPT = """You are a Principal Placement Evaluator and Technical Hiring Manager.
Your role is to analyze a student's quantitative diagnostic assessment and practice telemetry, identify technical strengths and critical skill gaps, and provide a clear, constructive, and actionable placement readiness evaluation.

Guidelines:
1. Provide an objective appraisal based strictly on observed accuracy and problem-solving velocity.
2. Clearly distinguish between concepts where the candidate is interview-ready versus topics requiring immediate remediation.
3. Keep the tone encouraging, professional, and career-focused.
"""


class PerformanceEvaluationAgent:
    """Agent that translates quantitative performance analytics into qualitative interview readiness appraisals."""

    def __init__(
        self,
        analytics_service: Optional[AnalyticsService] = None,
        mock_mode: Optional[bool] = None
    ):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.analytics = analytics_service or AnalyticsService()

    def evaluate_student(
        self,
        student_id: int,
        session: Optional[Session] = None
    ) -> PlacementReadinessEvaluation:
        """Generate comprehensive placement readiness appraisal combining math telemetry and qualitative AI critique."""
        db = session or self.analytics.session

        # 1. Fetch student profile
        profile = db.query(StudentProfile).filter_by(id=student_id).first()
        target_role = profile.target_role if profile else "Software Development Engineer (SDE)"

        # 2. Compute quantitative telemetry
        topic_masteries = self.analytics.get_topic_mastery_breakdown(student_id)
        radar_chart_data = self.analytics.get_radar_chart_data(topic_masteries)
        learning_velocity = self.analytics.calculate_learning_velocity(student_id)
        readiness_index = self.analytics.compute_placement_readiness_index(topic_masteries, target_role)

        # 3. Determine readiness tier
        if readiness_index >= 85.0:
            tier = "Interview Ready"
        elif readiness_index >= 70.0:
            tier = "Competitive"
        elif readiness_index >= 45.0:
            tier = "Early Stage"
        else:
            tier = "Not Ready"

        # 4. Identify Strengths and Critical Gaps
        strengths = [
            f"{t.topic} ({t.mastery_percentage:.0f}% mastery)"
            for t in topic_masteries
            if t.mastery_percentage >= 75.0 and (t.assessments_taken + t.practice_problems_solved) > 0
        ]
        critical_gaps = [
            f"{t.topic} ({t.mastery_percentage:.0f}% mastery)"
            for t in topic_masteries
            if t.mastery_percentage < 60.0 and (t.assessments_taken + t.practice_problems_solved) > 0
        ]
        # Include untested core domains in gaps
        untested = [
            t.topic for t in topic_masteries
            if (t.assessments_taken + t.practice_problems_solved) == 0
        ][:2]
        if untested:
            critical_gaps.extend([f"{u} (Untested)" for u in untested])

        # 5. Generate Qualitative Evaluation Summary
        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            summary, focus_areas = self._heuristic_mock_critique(
                target_role=target_role,
                readiness_index=readiness_index,
                tier=tier,
                strengths=strengths,
                gaps=critical_gaps,
                velocity=learning_velocity
            )
        else:
            try:
                summary, focus_areas = self._llm_critique(
                    target_role=target_role,
                    readiness_index=readiness_index,
                    tier=tier,
                    strengths=strengths,
                    gaps=critical_gaps,
                    velocity=learning_velocity
                )
            except Exception:
                summary, focus_areas = self._heuristic_mock_critique(
                    target_role=target_role,
                    readiness_index=readiness_index,
                    tier=tier,
                    strengths=strengths,
                    gaps=critical_gaps,
                    velocity=learning_velocity
                )

        return PlacementReadinessEvaluation(
            student_id=student_id,
            target_role=target_role,
            overall_readiness_index=readiness_index,
            readiness_tier=tier,
            topic_masteries=topic_masteries,
            radar_chart_data=radar_chart_data,
            learning_velocity=learning_velocity,
            strengths=strengths or ["Foundational engineering enthusiasm"],
            critical_gaps=critical_gaps or ["Complete comprehensive diagnostic tests"],
            qualitative_evaluation_summary=summary,
            recommended_focus_areas=focus_areas
        )

    def _heuristic_mock_critique(
        self,
        target_role: str,
        readiness_index: float,
        tier: str,
        strengths: List[str],
        gaps: List[str],
        velocity: LearningVelocity
    ) -> tuple[str, List[str]]:
        """Synthesize high-yield pedagogical critique deterministically with zero Azure token spend."""
        summary_lines = [
            f"Candidate is currently evaluated at the **{tier}** milestone with an overall readiness score of **{readiness_index:.1f}%** for target role: **{target_role}**.",
            f"- **Preparation Velocity**: Solving approximately **{velocity.problems_per_day:.1f} problems/day** with a **{velocity.trend.lower()}** momentum trend across a **{velocity.streak_days}-day** preparation streak.",
            f"- **Core Strengths**: Demonstrated solid technical mastery in {', '.join(strengths[:2]) if strengths else 'preliminary coursework'}.",
            f"- **High-Yield Remediation**: Focus immediate study cycles on remediating {', '.join(gaps[:2]) if gaps else 'breadth across core CS domains'}."
        ]
        summary = "\n".join(summary_lines)

        focus_areas = [
            "Complete dedicated diagnostic assessments for untested topics",
            "Drill 10-15 conceptual coding questions in high-priority weak areas",
            "Consult the RAG Tutor for algorithmic complexity and architectural tradeoffs"
        ]
        return summary, focus_areas

    def _llm_critique(
        self,
        target_role: str,
        readiness_index: float,
        tier: str,
        strengths: List[str],
        gaps: List[str],
        velocity: LearningVelocity
    ) -> tuple[str, List[str]]:
        """Call Azure OpenAI / Foundry model for qualitative assessment."""
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        user_content = json.dumps({
            "target_role": target_role,
            "readiness_index": readiness_index,
            "tier": tier,
            "strengths": strengths,
            "critical_gaps": gaps,
            "velocity": velocity.model_dump()
        }, indent=2)

        resp = client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Provide placement evaluation critique for candidate:\n{user_content}"}
            ],
            temperature=0.2,
            max_tokens=500
        )
        summary = resp.choices[0].message.content or "Placement evaluation synthesized."
        focus_areas = [
            "Strengthen core algorithms and data structures",
            "Focus on system concepts and database concurrency",
            "Maintain consistent daily coding practice"
        ]
        return summary, focus_areas
