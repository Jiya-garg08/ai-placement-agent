from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models.student import StudentProfile
from database.models.skill_gap import SkillGap
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.models.practice import PracticeStreak
from database.models.recommendation import NextBestAction
from schemas.recommendation_schema import ActionItem
from services.analytics_service import AnalyticsService


class NextActionService:
    """Surfaces 1-3 urgent, empirical next best actions based on diagnostic weak spots,

    skill gaps, and curriculum milestone progression.
    """

    def __init__(self, session: Optional[Session] = None, analytics_service: Optional[AnalyticsService] = None):
        self._owns_session = session is None
        self.session = session if session is not None else SessionLocal()
        self.analytics = analytics_service or AnalyticsService(session=self.session)

    def generate_next_actions(self, student_id: int) -> List[ActionItem]:
        """Generate and persist prioritized tactical next best actions for a candidate."""
        profile = self.session.query(StudentProfile).filter_by(id=student_id).first()
        target_role = profile.target_role if profile else "Software Development Engineer (SDE)"

        # 1. Fetch empirical topic masteries
        masteries = self.analytics.get_topic_mastery_breakdown(student_id)
        tested_masteries = [m for m in masteries if (m.assessments_taken + m.practice_problems_solved) > 0]
        tested_masteries.sort(key=lambda m: m.mastery_percentage)

        # 2. Fetch latest skill gap record if exists
        skill_gap = (
            self.session.query(SkillGap)
            .filter_by(profile_id=student_id)
            .order_by(SkillGap.created_at.desc())
            .first()
        )

        # 3. Fetch active learning plan if exists
        active_plan = (
            self.session.query(LearningPlan)
            .filter_by(profile_id=student_id, is_active=True)
            .first()
        )
        pending_plan_item = None
        if active_plan:
            pending_plan_item = (
                self.session.query(LearningPlanItem)
                .filter(LearningPlanItem.plan_id == active_plan.id, LearningPlanItem.status != "Completed")
                .order_by(LearningPlanItem.week_number.asc(), LearningPlanItem.order_index.asc())
                .first()
            )

        actions: List[ActionItem] = []

        # ----------------------------------------------------------------------
        # ACTION 1: Weak Spot Remediation (Drill or Practice)
        # ----------------------------------------------------------------------
        if tested_masteries and tested_masteries[0].mastery_percentage < 70.0:
            weakest = tested_masteries[0]
            actions.append(
                ActionItem(
                    action_type="PRACTICE_DRILL",
                    title=f"Practice 5 Interview Questions in {weakest.topic}",
                    description=f"Your measured mastery in {weakest.topic} is currently {weakest.mastery_percentage:.0f}%. Strengthen your accuracy with targeted MCQs.",
                    topic=weakest.topic,
                    priority="HIGH",
                    estimated_minutes=15,
                    target_page="Practice",
                    action_payload={"topic": weakest.topic, "action": "drill"},
                    reasoning=f"Empirical diagnostic scores identified {weakest.topic} as your primary weak area."
                )
            )
        elif skill_gap and skill_gap.weak_skills:
            weak_name = skill_gap.weak_skills[0].split(" (")[0]
            actions.append(
                ActionItem(
                    action_type="PRACTICE_DRILL",
                    title=f"Drill Practice Problems in {weak_name}",
                    description=f"Triangulated gap analysis flagged {weak_name} as a weak requirement for {target_role}.",
                    topic=weak_name,
                    priority="HIGH",
                    estimated_minutes=15,
                    target_page="Practice",
                    action_payload={"topic": weak_name, "action": "drill"},
                    reasoning=f"{weak_name} was detected as a weak competency required by your target job description."
                )
            )
        else:
            # If no tested weak spot yet, recommend diagnostic assessment
            actions.append(
                ActionItem(
                    action_type="DIAGNOSTIC_TEST",
                    title="Take 10-Question Diagnostic Assessment",
                    description=f"Calibrate your conceptual readiness across core domains for {target_role}.",
                    topic="Data Structures & Algorithms",
                    priority="HIGH",
                    estimated_minutes=20,
                    target_page="Assessments",
                    action_payload={"role": target_role},
                    reasoning="Diagnostic assessment is needed to calibrate your personalized skill gap matrix."
                )
            )

        # ----------------------------------------------------------------------
        # ACTION 2: Missing Skill Pedagogical Deep-Dive (RAG Tutor)
        # ----------------------------------------------------------------------
        if skill_gap and skill_gap.missing_skills:
            missing_topic = skill_gap.missing_skills[0]
            actions.append(
                ActionItem(
                    action_type="TUTOR_REVIEW",
                    title=f"Review High-Yield Concepts for {missing_topic}",
                    description=f"Ask the grounded RAG Tutor to explain key principles, edge cases, and interview patterns for {missing_topic}.",
                    topic=missing_topic,
                    priority="MEDIUM",
                    estimated_minutes=15,
                    target_page="Tutor",
                    action_payload={"query": f"Explain key interview concepts in {missing_topic}", "topic": missing_topic},
                    reasoning=f"{missing_topic} is a mandatory requirement for {target_role} currently absent from your resume."
                )
            )
        elif tested_masteries and len(tested_masteries) > 1 and tested_masteries[1].mastery_percentage < 75.0:
            second_weak = tested_masteries[1]
            actions.append(
                ActionItem(
                    action_type="TUTOR_REVIEW",
                    title=f"Consult Tutor on {second_weak.topic} Tradeoffs",
                    description=f"Deep-dive into complexity profiles and invariants for {second_weak.topic}.",
                    topic=second_weak.topic,
                    priority="MEDIUM",
                    estimated_minutes=15,
                    target_page="Tutor",
                    action_payload={"topic": second_weak.topic},
                    reasoning=f"{second_weak.topic} mastery is at {second_weak.mastery_percentage:.0f}%, which can be elevated through cited tutoring."
                )
            )
        else:
            actions.append(
                ActionItem(
                    action_type="TUTOR_REVIEW",
                    title="Review Operating Systems & Concurrency Invariants",
                    description="Explore thread synchronization, semaphores, and virtual memory concepts with verified citations.",
                    topic="Operating Systems",
                    priority="MEDIUM",
                    estimated_minutes=15,
                    target_page="Tutor",
                    action_payload={"topic": "Operating Systems"},
                    reasoning="Operating Systems questions frequently decide interview shortlists for Tier 1 engineering roles."
                )
            )

        # ----------------------------------------------------------------------
        # ACTION 3: Preparation Roadmap Milestone or Coding Challenge
        # ----------------------------------------------------------------------
        if pending_plan_item:
            actions.append(
                ActionItem(
                    action_type="ROADMAP_MILESTONE",
                    title=f"Complete Week {pending_plan_item.week_number} Milestone: {pending_plan_item.topic}",
                    description=f"Milestone goal: {pending_plan_item.learning_objectives} (Target: {pending_plan_item.practice_goal_count} problems).",
                    topic=pending_plan_item.topic,
                    priority="MEDIUM",
                    estimated_minutes=30,
                    target_page="Roadmap",
                    action_payload={"plan_id": active_plan.id, "item_id": pending_plan_item.id},
                    reasoning="Consistent chronological progression along your 4-week preparation plan ensures comprehensive coverage."
                )
            )
        else:
            actions.append(
                ActionItem(
                    action_type="PRACTICE_DRILL",
                    title="Solve Featured Algorithmic Coding Challenge",
                    description="Tackle two-pointer or hash map problems to maintain your active preparation streak.",
                    topic="Data Structures & Algorithms",
                    priority="LOW",
                    estimated_minutes=20,
                    target_page="Practice",
                    action_payload={"snippet_id": "dsa-01-two-sum"},
                    reasoning="Daily algorithmic coding maintains muscle memory and extends your preparation streak."
                )
            )

        # 4. Persist generated actions
        self._persist_actions(student_id, actions)

        return actions[:3]

    def _persist_actions(self, student_id: int, actions: List[ActionItem]) -> None:
        """Persist fresh actions into next_best_actions table."""
        # Remove previous uncompleted actions to prevent stale recommendations
        self.session.query(NextBestAction).filter_by(student_id=student_id, is_completed=False).delete()

        for a in actions[:3]:
            record = NextBestAction(
                student_id=student_id,
                action_type=a.action_type,
                title=a.title,
                description=a.description,
                topic=a.topic,
                priority=a.priority,
                estimated_minutes=a.estimated_minutes,
                target_page=a.target_page,
                action_payload=a.action_payload,
                is_completed=False
            )
            self.session.add(record)
            self.session.flush()
            a.id = record.id

        self.session.commit()

    def mark_action_completed(self, action_id: int) -> bool:
        """Transition an action to completed status."""
        action = self.session.query(NextBestAction).filter_by(id=action_id).first()
        if not action:
            return False
        action.is_completed = True
        action.completed_at = datetime.now(timezone.utc)
        self.session.commit()
        return True

    def get_saved_actions(self, student_id: int) -> List[NextBestAction]:
        """Fetch active recommendations from the database."""
        return (
            self.session.query(NextBestAction)
            .filter_by(student_id=student_id)
            .order_by(NextBestAction.is_completed.asc(), NextBestAction.created_at.desc())
            .limit(5)
            .all()
        )
