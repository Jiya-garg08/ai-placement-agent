from typing import Dict, Any, List, Optional
from database.database import SessionLocal
from database.repositories.attempt_repository import AssessmentAttemptRepository
from database.repositories.plan_repository import LearningPlanRepository
from database.repositories.student_repository import StudentProfileRepository


def get_student_performance_summary(student_id: int) -> Dict[str, Any]:
    """
    MCP Tool: Retrieve aggregated student assessment performance, accuracy, and topic weak spots.

    Args:
        student_id: The unique primary key ID of the student user.

    Returns:
        JSON object with total quizzes, average score, topic mastery map, and top weakest topics.
    """
    db = SessionLocal()
    try:
        profile_repo = StudentProfileRepository(db)
        profile = profile_repo.get_by_user_id(student_id)
        if not profile:
            return {"status": "error", "message": f"Profile for student ID {student_id} not found."}

        attempt_repo = AssessmentAttemptRepository(db)
        attempts = attempt_repo.get_attempts_for_profile(profile.id)

        if not attempts:
            return {
                "status": "success",
                "student_id": student_id,
                "total_quizzes_completed": 0,
                "overall_accuracy_percentage": 0.0,
                "topic_mastery": {},
                "weakest_topics": [],
                "strongest_topics": [],
                "message": "No assessments completed yet."
            }

        total_correct = sum(a.total_correct for a in attempts)
        total_questions = sum(a.total_questions for a in attempts) or 1
        overall_accuracy = round((total_correct / total_questions) * 100, 2)

        mastery_map = attempt_repo.get_aggregated_topic_mastery(profile.id)

        # Sort topics by accuracy ascending for weak topics, descending for strong
        sorted_topics = sorted(mastery_map.items(), key=lambda item: item[1])
        weakest = [f"{t} ({p}%)" for t, p in sorted_topics if p < 60.0][:3]
        strongest = [f"{t} ({p}%)" for t, p in sorted(mastery_map.items(), key=lambda item: item[1], reverse=True) if p >= 70.0][:3]

        return {
            "status": "success",
            "student_id": student_id,
            "total_quizzes_completed": len(attempts),
            "overall_accuracy_percentage": overall_accuracy,
            "topic_mastery": mastery_map,
            "weakest_topics": weakest,
            "strongest_topics": strongest
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve performance summary: {str(e)}"}
    finally:
        db.close()


def get_active_learning_roadmap(student_id: int) -> Dict[str, Any]:
    """
    MCP Tool: Retrieve the active week-by-week learning roadmap and milestone progress.

    Args:
        student_id: The unique primary key ID of the student user.

    Returns:
        JSON object containing roadmap metadata and ordered milestone items.
    """
    db = SessionLocal()
    try:
        profile_repo = StudentProfileRepository(db)
        profile = profile_repo.get_by_user_id(student_id)
        if not profile:
            return {"status": "error", "message": f"Profile for student ID {student_id} not found."}

        plan_repo = LearningPlanRepository(db)
        plan = plan_repo.get_active_plan(profile.id)

        if not plan:
            return {
                "status": "success",
                "student_id": student_id,
                "has_active_plan": False,
                "message": "No active learning plan found. Please generate a plan first."
            }

        items = [
            {
                "id": item.id,
                "week_number": item.week_number,
                "order_index": item.order_index,
                "topic": item.topic,
                "priority": item.priority,
                "learning_objectives": item.learning_objectives,
                "practice_goal_count": item.practice_goal_count,
                "status": item.status
            }
            for item in plan.items
        ]

        completed_count = sum(1 for i in items if i["status"] == "Completed")
        progress_pct = round((completed_count / max(len(items), 1)) * 100, 1)

        return {
            "status": "success",
            "student_id": student_id,
            "has_active_plan": True,
            "plan_id": plan.id,
            "plan_name": plan.plan_name,
            "target_role": plan.target_role,
            "total_weeks": plan.total_weeks,
            "daily_hours_target": plan.daily_hours_target,
            "progress_percentage": progress_pct,
            "items": items
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve learning roadmap: {str(e)}"}
    finally:
        db.close()


def mark_roadmap_item_status(item_id: int, status: str) -> Dict[str, Any]:
    """
    MCP Tool: Update the completion status of a specific roadmap topic.

    Args:
        item_id: The unique primary key ID of the LearningPlanItem.
        status: One of 'Pending', 'In Progress', or 'Completed'.

    Returns:
        JSON object confirming the milestone status transition.
    """
    if status not in ("Pending", "In Progress", "Completed"):
        return {"status": "error", "message": f"Invalid status '{status}'. Must be Pending, In Progress, or Completed."}

    db = SessionLocal()
    try:
        plan_repo = LearningPlanRepository(db)
        updated = plan_repo.update_item_status(item_id, status)
        if not updated:
            return {"status": "error", "message": f"Roadmap item with ID {item_id} not found."}

        return {
            "status": "success",
            "item_id": updated.id,
            "topic": updated.topic,
            "new_status": updated.status,
            "message": f"Item '{updated.topic}' updated to '{updated.status}'."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to update roadmap item: {str(e)}"}
    finally:
        db.close()
