from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database.models.assessment import Assessment, Question
from database.repositories.base_repository import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    """Repository for querying placement question bank."""

    def __init__(self, session: Session):
        super().__init__(Question, session)

    def get_by_topic(self, topic: str, limit: int = 10) -> List[Question]:
        """Fetch questions for a specific topic."""
        return self.session.query(Question).filter(Question.topic == topic).limit(limit).all()

    def sample_questions_for_role(self, topics: List[str], total_count: int = 10) -> List[Question]:
        """Sample balanced questions randomly across requested topics, prioritizing role competencies."""
        from sqlalchemy import or_
        questions = []
        count_per_topic = max(1, total_count // len(topics)) if topics else total_count

        for topic in topics:
            sampled = self.session.query(Question).filter(
                Question.topic.ilike(f"%{topic}%")
            ).order_by(func.random()).limit(count_per_topic).all()
            questions.extend(sampled)

        # 1. If we need more to reach total_count, fill first from the requested topics
        if len(questions) < total_count and topics:
            existing_ids = [q.id for q in questions]
            topic_filters = [Question.topic.ilike(f"%{t}%") for t in topics]
            topic_filler = self.session.query(Question).filter(
                or_(*topic_filters),
                ~Question.id.in_(existing_ids) if existing_ids else True
            ).order_by(func.random()).limit(total_count - len(questions)).all()
            questions.extend(topic_filler)

        # 2. Only if still fewer than total_count, fill with general placement questions
        if len(questions) < total_count:
            existing_ids = [q.id for q in questions]
            filler = self.session.query(Question).filter(
                ~Question.id.in_(existing_ids) if existing_ids else True
            ).order_by(func.random()).limit(total_count - len(questions)).all()
            questions.extend(filler)

        return questions[:total_count]


class AssessmentRepository(BaseRepository[Assessment]):
    """Repository for managing diagnostic assessments."""

    def __init__(self, session: Session):
        super().__init__(Assessment, session)

    def get_with_questions(self, assessment_id: int) -> Optional[Assessment]:
        """Fetch assessment eager-loading its linked questions."""
        return self.session.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_latest_by_role(self, target_role: str) -> Optional[Assessment]:
        """Fetch the latest assessment tailored for a specific role."""
        return self.session.query(Assessment).filter(
            Assessment.target_role.ilike(f"%{target_role}%")
        ).order_by(Assessment.id.desc()).first()
