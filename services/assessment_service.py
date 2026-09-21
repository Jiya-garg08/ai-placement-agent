from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database.models.assessment import Assessment, Question
from database.repositories.assessment_repository import AssessmentRepository, QuestionRepository
from schemas.assessment_schema import (
    AssessmentSubmission,
    AssessmentResultResponse,
    TopicScore
)

# Mapping of target roles to primary technical evaluation topics
ROLE_TOPIC_MAP = {
    "Software Development Engineer (SDE)": [
        "Data Structures & Algorithms", "Database Management Systems", "SQL", "Operating Systems", "Computer Networks", "Java", "Python"
    ],
    "Backend Engineer": [
        "Database Management Systems", "SQL", "Operating Systems", "Computer Networks", "Data Structures & Algorithms", "Python"
    ],
    "Frontend Engineer": [
        "Object-Oriented Programming", "Computer Networks", "Data Structures & Algorithms"
    ],
    "Data Engineer": [
        "SQL", "Database Management Systems", "Python", "Data Structures & Algorithms"
    ],
    "Machine Learning Engineer": [
        "Machine Learning", "Python", "Data Structures & Algorithms", "SQL"
    ]
}


class AssessmentService:
    """Service handling assessment creation, question sampling, and submission evaluation."""

    def __init__(self, session: Session):
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.question_repo = QuestionRepository(session)

    def create_diagnostic_assessment(self, target_role: str, total_questions: int = 10) -> Assessment:
        """Generate a role-tailored diagnostic quiz sampling from relevant domain topics."""
        topics = ROLE_TOPIC_MAP.get(target_role, [
            "Data Structures & Algorithms", "Database Management Systems", "Operating Systems", "SQL", "Computer Networks"
        ])
        
        sampled_questions = self.question_repo.sample_questions_for_role(topics, total_count=total_questions)

        assessment = Assessment(
            title=f"Diagnostic Placement Assessment - {target_role}",
            target_role=target_role,
            topic="Core Technical Diagnostic",
            difficulty="Calibrated",
            total_questions=len(sampled_questions),
            time_limit_mins=20
        )
        
        for q in sampled_questions:
            assessment.questions.append(q)

        return self.assessment_repo.create(assessment)

    def get_assessment(self, assessment_id: int) -> Optional[Assessment]:
        """Fetch an assessment along with its questions."""
        return self.assessment_repo.get_with_questions(assessment_id)

    def evaluate_submission(self, submission: AssessmentSubmission, attempt_id: int = 1) -> AssessmentResultResponse:
        """Evaluate student answers against objective answer keys and compute topic scores."""
        assessment = self.get_assessment(submission.assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {submission.assessment_id} not found.")

        # Create quick lookup for question key and topic
        q_map: Dict[int, Question] = {q.id: q for q in assessment.questions}
        
        total_correct = 0
        topic_stats: Dict[str, Dict[str, int]] = {}

        for ans in submission.answers:
            q = q_map.get(ans.question_id)
            if not q:
                continue

            if q.topic not in topic_stats:
                topic_stats[q.topic] = {"correct": 0, "total": 0}
            topic_stats[q.topic]["total"] += 1

            if ans.selected_option_index == q.correct_option_index:
                total_correct += 1
                topic_stats[q.topic]["correct"] += 1

        total_questions = len(assessment.questions) or 1
        score_pct = round((total_correct / total_questions) * 100, 2)

        topic_breakdown = [
            TopicScore(
                topic=t,
                correct=stats["correct"],
                total=stats["total"],
                percentage=round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0.0
            )
            for t, stats in topic_stats.items()
        ]

        return AssessmentResultResponse(
            attempt_id=attempt_id,
            assessment_id=assessment.id,
            profile_id=submission.profile_id,
            total_questions=total_questions,
            total_correct=total_correct,
            score_percentage=score_pct,
            topic_breakdown=topic_breakdown
        )
