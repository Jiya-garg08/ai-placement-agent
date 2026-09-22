import json
from typing import Optional, List, Dict, Any

from config.settings import settings
from database.models.skill_gap import SkillGap
from schemas.plan_schema import LearningPlanStructure, LearningPlanItemSchema

PLANNER_SYSTEM_PROMPT = """You are an elite Placement Coach and Curriculum Architect.
Your role is to design an adaptive, highly structured, week-by-week placement preparation roadmap for a candidate based on their diagnostic test performance, missing job requirements, and weak technical topics.

Guidelines:
1. Schedule high-urgency weak skills and missing mandatory requirements in Week 1 and Week 2.
2. Ensure each milestone has concrete learning objectives and a specific practice target count (e.g. 15 problems).
3. Progression should build from foundational gap remediation to advanced problem-solving and mock assessments.
4. Output strictly valid JSON conforming to LearningPlanStructure."""


class LearningPlannerAgent:
    """Agent that synthesizes skill gaps and role targets into an actionable chronological preparation plan."""

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE

    def generate_plan(
        self,
        target_role: str,
        skill_gap: Optional[SkillGap] = None,
        total_weeks: int = 4,
        daily_hours: float = 2.5
    ) -> LearningPlanStructure:
        """Generate a structured personalized learning roadmap."""
        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            return self._heuristic_mock_generate(target_role, skill_gap, total_weeks, daily_hours)

        try:
            return self._llm_generate(target_role, skill_gap, total_weeks, daily_hours)
        except Exception:
            # Fallback gracefully to offline generator
            return self._heuristic_mock_generate(target_role, skill_gap, total_weeks, daily_hours)

    def _llm_generate(
        self,
        target_role: str,
        skill_gap: Optional[SkillGap],
        total_weeks: int,
        daily_hours: float
    ) -> LearningPlanStructure:
        """Call Azure OpenAI / Foundry model with structured Pydantic schema parsing."""
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        context = {
            "target_role": target_role,
            "total_weeks": total_weeks,
            "daily_hours_target": daily_hours,
            "weak_skills": skill_gap.weak_skills if skill_gap else [],
            "missing_skills": skill_gap.missing_skills if skill_gap else [],
            "priority_topics": skill_gap.priority_topics if skill_gap else [],
            "strong_skills": skill_gap.strong_skills if skill_gap else []
        }

        response = client.beta.chat.completions.parse(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a personalized preparation roadmap:\n{json.dumps(context, indent=2)}"}
            ],
            response_format=LearningPlanStructure,
            temperature=0.2
        )
        return response.choices[0].message.parsed

    def _heuristic_mock_generate(
        self,
        target_role: str,
        skill_gap: Optional[SkillGap],
        total_weeks: int,
        daily_hours: float
    ) -> LearningPlanStructure:
        """Construct high-yield, calibrated curriculum deterministically."""
        items: List[LearningPlanItemSchema] = []

        # Extract top priorities from skill_gap
        priority_topics = [
            p["topic"] if isinstance(p, dict) else str(p)
            for p in (skill_gap.priority_topics if skill_gap else [])
        ]
        weak_topics = [w.split(" (")[0] for w in (skill_gap.weak_skills if skill_gap else [])]
        missing_topics = skill_gap.missing_skills if skill_gap else []

        # Ensure we have representative topics
        all_remediation = []
        for t in weak_topics + missing_topics + priority_topics:
            if t not in all_remediation:
                all_remediation.append(t)
        
        if not all_remediation:
            all_remediation = ["Data Structures & Algorithms", "SQL & DBMS", "Operating Systems", "System Design"]

        order = 1
        # Week 1: Remediate top weak areas
        w1_topic = all_remediation[0] if len(all_remediation) > 0 else "Data Structures & Algorithms"
        items.append(LearningPlanItemSchema(
            week_number=1,
            order_index=order,
            topic=w1_topic,
            subtopics=["Core Foundations", "Problem Solving Patterns", "Standard Interview Questions"],
            priority="High",
            learning_objectives=f"Remediate baseline diagnostic deficiencies in {w1_topic}. Master core principles and edge-case handling.",
            practice_goal_count=15,
            status="In Progress"
        ))
        order += 1

        # Week 2: Bridge missing requirements
        w2_topic = all_remediation[1] if len(all_remediation) > 1 else "Database Management Systems & SQL"
        items.append(LearningPlanItemSchema(
            week_number=2,
            order_index=order,
            topic=w2_topic,
            subtopics=["ACID Properties", "Complex Queries & Joins", "Indexing & Optimization"],
            priority="High",
            learning_objectives=f"Close critical knowledge gap in {w2_topic} required by target job descriptions.",
            practice_goal_count=15,
            status="Pending"
        ))
        order += 1

        # Week 3: Systems & Core CS Concepts
        w3_topic = all_remediation[2] if len(all_remediation) > 2 else "Operating Systems & Computer Networks"
        items.append(LearningPlanItemSchema(
            week_number=3,
            order_index=order,
            topic=w3_topic,
            subtopics=["Processes & Threads", "Memory Management", "TCP/IP Protocol Stack"],
            priority="Medium",
            learning_objectives=f"Strengthen depth in {w3_topic} to excel in technical interview rounds.",
            practice_goal_count=12,
            status="Pending"
        ))
        order += 1

        # Week 4: Comprehensive Mock Interviews & Speed Practice
        items.append(LearningPlanItemSchema(
            week_number=4,
            order_index=order,
            topic="Placement Mock Assessments & Final Review",
            subtopics=["Full Diagnostic Retest", "Time Management", "Behavioral & Tech Interview Prep"],
            priority="High",
            learning_objectives="Synthesize all learned domains under timed interview conditions to maximize placement conversion.",
            practice_goal_count=20,
            status="Pending"
        ))

        return LearningPlanStructure(
            plan_name=f"{total_weeks}-Week Placement Accelerator: {target_role}",
            target_role=target_role,
            total_weeks=total_weeks,
            daily_hours_target=daily_hours,
            items=items
        )
