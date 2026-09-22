from typing import Optional, List
from sqlalchemy.orm import Session
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.repositories.base_repository import BaseRepository
from schemas.plan_schema import LearningPlanStructure


class LearningPlanRepository(BaseRepository[LearningPlan]):
    """Repository for managing personalized learning plans and milestones."""

    def __init__(self, session: Session):
        super().__init__(LearningPlan, session)

    def get_active_plan(self, profile_id: int) -> Optional[LearningPlan]:
        """Fetch the currently active learning plan with eager-loaded items for a student."""
        return self.session.query(LearningPlan).filter(
            LearningPlan.profile_id == profile_id,
            LearningPlan.is_active == True
        ).first()

    def deactivate_existing_plans(self, profile_id: int):
        """Mark any existing active plans for the student as inactive."""
        self.session.query(LearningPlan).filter(
            LearningPlan.profile_id == profile_id,
            LearningPlan.is_active == True
        ).update({"is_active": False})
        self.session.commit()

    def create_plan_with_items(self, profile_id: int, structure: LearningPlanStructure) -> LearningPlan:
        """Deactivate old plans and persist a new learning plan with its ordered items."""
        self.deactivate_existing_plans(profile_id)

        plan = LearningPlan(
            profile_id=profile_id,
            plan_name=structure.plan_name,
            target_role=structure.target_role,
            total_weeks=structure.total_weeks,
            daily_hours_target=structure.daily_hours_target,
            is_active=True
        )
        self.session.add(plan)
        self.session.flush()  # Generate plan.id

        for item_data in structure.items:
            item = LearningPlanItem(
                plan_id=plan.id,
                week_number=item_data.week_number,
                order_index=item_data.order_index,
                topic=item_data.topic,
                subtopics=item_data.subtopics,
                priority=item_data.priority,
                learning_objectives=item_data.learning_objectives,
                practice_goal_count=item_data.practice_goal_count,
                status=item_data.status
            )
            self.session.add(item)

        self.session.commit()
        self.session.refresh(plan)
        return plan

    def update_item_status(self, item_id: int, status: str) -> Optional[LearningPlanItem]:
        """Update the completion status of a specific roadmap item."""
        item = self.session.query(LearningPlanItem).filter(LearningPlanItem.id == item_id).first()
        if item:
            item.status = status
            self.session.commit()
            self.session.refresh(item)
            return item
        return None
