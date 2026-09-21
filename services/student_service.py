from typing import Optional, Tuple
from sqlalchemy.orm import Session
from database.models.student import User, StudentProfile
from database.repositories.student_repository import UserRepository, StudentProfileRepository
from schemas.profile_schema import StudentOnboardingRequest, StudentProfileUpdate


class StudentService:
    """Service handling student registration, onboarding, and profile management."""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.profile_repo = StudentProfileRepository(session)

    def onboard_student(self, data: StudentOnboardingRequest) -> Tuple[User, StudentProfile]:
        """
        Onboard a student: check if email exists, create User and associated StudentProfile.
        If user already exists, update profile details.
        """
        user = self.user_repo.get_by_email(data.email)
        if not user:
            user = User(
                email=data.email.lower().strip(),
                name=data.name.strip()
            )
            user = self.user_repo.create(user)

        profile = self.profile_repo.get_by_user_id(user.id)
        if not profile:
            profile = StudentProfile(
                user_id=user.id,
                target_role=data.target_role,
                career_goal=data.career_goal,
                target_company_tier=data.target_company_tier,
                college=data.college,
                graduation_year=data.graduation_year,
                current_semester=data.current_semester,
                primary_skills=data.primary_skills or []
            )
            profile = self.profile_repo.create(profile)
        else:
            # Update existing profile
            update_dict = {
                "target_role": data.target_role,
                "career_goal": data.career_goal,
                "target_company_tier": data.target_company_tier,
                "college": data.college,
                "graduation_year": data.graduation_year,
                "current_semester": data.current_semester,
                "primary_skills": data.primary_skills
            }
            profile = self.profile_repo.update(profile, update_dict)

        return user, profile

    def get_student_by_user_id(self, user_id: int) -> Optional[Tuple[User, Optional[StudentProfile]]]:
        """Fetch user and attached profile by user ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        profile = self.profile_repo.get_by_user_id(user_id)
        return user, profile

    def update_profile(self, user_id: int, updates: StudentProfileUpdate) -> Optional[StudentProfile]:
        """Update fields of an existing student profile."""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return None
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        return self.profile_repo.update(profile, update_data)
