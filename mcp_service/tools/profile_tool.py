from typing import Optional, Dict, Any
from database.database import SessionLocal
from database.repositories.student_repository import UserRepository, StudentProfileRepository


def get_student_profile(student_id: int) -> Dict[str, Any]:
    """
    MCP Tool: Retrieve the candidate's profile, academic background, and declared skills.

    Args:
        student_id: The unique primary key ID of the student user.

    Returns:
        JSON object containing student credentials, career targets, and skills.
    """
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        profile_repo = StudentProfileRepository(db)

        user = user_repo.get_by_id(student_id)
        if not user:
            return {"status": "error", "message": f"Student with ID {student_id} not found."}

        profile = profile_repo.get_by_user_id(user.id)
        return {
            "status": "success",
            "student_id": user.id,
            "name": user.name,
            "email": user.email,
            "target_role": profile.target_role if profile else "Software Development Engineer (SDE)",
            "career_goal": profile.career_goal if profile else None,
            "target_company_tier": profile.target_company_tier if profile else "Tier 1 / Product",
            "college": profile.college if profile else None,
            "graduation_year": profile.graduation_year if profile else None,
            "primary_skills": profile.primary_skills if profile else []
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve student profile: {str(e)}"}
    finally:
        db.close()


def update_student_target_role(
    student_id: int,
    target_role: str,
    target_company_tier: Optional[str] = "Tier 1 / Product"
) -> Dict[str, Any]:
    """
    MCP Tool: Update a student's target placement role and company tier preferences.

    Args:
        student_id: The unique primary key ID of the student.
        target_role: The desired engineering role (e.g. 'Software Development Engineer', 'Data Engineer').
        target_company_tier: Desired company classification (e.g. 'Tier 1 / Product', 'Fintech', 'FAANG').

    Returns:
        JSON object confirming the update and echoing the new profile values.
    """
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        profile_repo = StudentProfileRepository(db)

        user = user_repo.get_by_id(student_id)
        if not user:
            return {"status": "error", "message": f"Student with ID {student_id} not found."}

        profile = profile_repo.get_by_user_id(user.id)
        if not profile:
            return {"status": "error", "message": f"Profile not found for student ID {student_id}."}

        updates = {"target_role": target_role.strip()}
        if target_company_tier:
            updates["target_company_tier"] = target_company_tier.strip()

        updated = profile_repo.update(profile, updates)
        return {
            "status": "success",
            "student_id": user.id,
            "target_role": updated.target_role,
            "target_company_tier": updated.target_company_tier,
            "message": "Student target role updated successfully."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to update target role: {str(e)}"}
    finally:
        db.close()
