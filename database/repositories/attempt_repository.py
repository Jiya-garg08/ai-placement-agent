from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from database.models.assessment_attempt import AssessmentAttempt, AssessmentAnswer
from database.repositories.base_repository import BaseRepository


class AssessmentAttemptRepository(BaseRepository[AssessmentAttempt]):
    """Repository for managing student assessment attempts and performance telemetry."""

    def __init__(self, session: Session):
        super().__init__(AssessmentAttempt, session)

    def get_attempts_for_profile(self, profile_id: int) -> List[AssessmentAttempt]:
        """Fetch all assessment attempts for a student ordered by most recent."""
        return self.session.query(AssessmentAttempt).filter(
            AssessmentAttempt.profile_id == profile_id
        ).order_by(AssessmentAttempt.id.desc()).all()

    def get_latest_attempt(self, profile_id: int) -> Optional[AssessmentAttempt]:
        """Fetch the single most recent assessment attempt for a student."""
        return self.session.query(AssessmentAttempt).filter(
            AssessmentAttempt.profile_id == profile_id
        ).order_by(AssessmentAttempt.id.desc()).first()

    def get_aggregated_topic_mastery(self, profile_id: int) -> Dict[str, float]:
        """
        Aggregate topic percentages across all completed attempts for a student.
        Returns a map: {topic: average_percentage_score}.
        """
        attempts = self.get_attempts_for_profile(profile_id)
        if not attempts:
            return {}

        topic_totals: Dict[str, Dict[str, int]] = {}
        for att in attempts:
            for item in att.topic_scores:
                t = item.get("topic")
                c = item.get("correct", 0)
                tot = item.get("total", 0)
                if t:
                    if t not in topic_totals:
                        topic_totals[t] = {"correct": 0, "total": 0}
                    topic_totals[t]["correct"] += c
                    topic_totals[t]["total"] += tot

        return {
            topic: round((data["correct"] / data["total"]) * 100, 2) if data["total"] > 0 else 0.0
            for topic, data in topic_totals.items()
        }


class AssessmentAnswerRepository(BaseRepository[AssessmentAnswer]):
    """Repository for individual answer records."""

    def __init__(self, session: Session):
        super().__init__(AssessmentAnswer, session)

    def get_by_attempt_id(self, attempt_id: int) -> List[AssessmentAnswer]:
        """Fetch all answers for a specific attempt."""
        return self.session.query(AssessmentAnswer).filter(AssessmentAnswer.attempt_id == attempt_id).all()
