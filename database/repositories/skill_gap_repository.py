from typing import Optional
from sqlalchemy.orm import Session
from database.models.skill_gap import SkillGap
from database.repositories.base_repository import BaseRepository


class SkillGapRepository(BaseRepository[SkillGap]):
    """Repository for managing triangulated skill gap records."""

    def __init__(self, session: Session):
        super().__init__(SkillGap, session)

    def get_latest_for_profile(self, profile_id: int) -> Optional[SkillGap]:
        """Fetch the most recent skill gap evaluation for a student profile."""
        return self.session.query(SkillGap).filter(
            SkillGap.profile_id == profile_id
        ).order_by(SkillGap.id.desc()).first()
