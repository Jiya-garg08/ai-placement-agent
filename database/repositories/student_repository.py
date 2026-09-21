from typing import Optional
from sqlalchemy.orm import Session
from database.models.student import User, StudentProfile
from database.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for managing User account records."""

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user record by unique email address."""
        return self.session.query(User).filter(User.email == email.lower()).first()


class StudentProfileRepository(BaseRepository[StudentProfile]):
    """Repository for managing student placement profiles."""

    def __init__(self, session: Session):
        super().__init__(StudentProfile, session)

    def get_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        """Fetch the student profile associated with a specific user ID."""
        return self.session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
