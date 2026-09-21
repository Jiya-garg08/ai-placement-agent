from typing import Optional, List
from sqlalchemy.orm import Session
from database.models.resume import Resume, JobDescription
from database.repositories.base_repository import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Repository for managing student resume records."""

    def __init__(self, session: Session):
        super().__init__(Resume, session)

    def get_by_profile_id(self, profile_id: int) -> List[Resume]:
        """Fetch all resumes uploaded for a student profile."""
        return self.session.query(Resume).filter(Resume.profile_id == profile_id).order_by(Resume.id.desc()).all()

    def get_latest_for_profile(self, profile_id: int) -> Optional[Resume]:
        """Fetch the most recently uploaded resume for a student profile."""
        return self.session.query(Resume).filter(Resume.profile_id == profile_id).order_by(Resume.id.desc()).first()


class JobDescriptionRepository(BaseRepository[JobDescription]):
    """Repository for managing targeted job descriptions."""

    def __init__(self, session: Session):
        super().__init__(JobDescription, session)

    def get_by_profile_id(self, profile_id: int) -> List[JobDescription]:
        """Fetch all target job descriptions for a student profile."""
        return self.session.query(JobDescription).filter(JobDescription.profile_id == profile_id).order_by(JobDescription.id.desc()).all()

    def get_latest_for_profile(self, profile_id: int) -> Optional[JobDescription]:
        """Fetch the most recent target job description for a student profile."""
        return self.session.query(JobDescription).filter(JobDescription.profile_id == profile_id).order_by(JobDescription.id.desc()).first()
