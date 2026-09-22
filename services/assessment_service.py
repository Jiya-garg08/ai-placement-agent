from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database.models.assessment import Assessment, Question
from database.models.assessment_attempt import AssessmentAttempt, AssessmentAnswer
from database.repositories.assessment_repository import AssessmentRepository, QuestionRepository
from database.repositories.attempt_repository import AssessmentAttemptRepository, AssessmentAnswerRepository
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


from database.database import SessionLocal


class AssessmentService:
    """Service handling assessment creation, question sampling, and submission evaluation."""

    def __init__(self, session: Optional[Session] = None):
        self._owns_session = session is None
        self.session = session if session is not None else SessionLocal()
        self.assessment_repo = AssessmentRepository(self.session)
        self.question_repo = QuestionRepository(self.session)
        self.attempt_repo = AssessmentAttemptRepository(self.session)
        self.answer_repo = AssessmentAnswerRepository(self.session)

    @classmethod
    def resolve_topics_for_role_and_skills(
        cls,
        target_role: str,
        candidate_skills: Optional[List[str]] = None,
        resume_skills: Optional[List[str]] = None
    ) -> List[str]:
        """Dynamically resolve technical evaluation topics tailored to role, primary skills, and resume requirements."""
        role_lower = (target_role or "").lower()
        topics: List[str] = []

        # 1. Match role archetypes
        if any(kw in role_lower for kw in ["machine learning", "data scientist", "ai engineer", "ml engineer"]):
            topics.extend(["Machine Learning", "Data Science", "Python", "SQL"])
        elif any(kw in role_lower for kw in ["product manager", "apm", "product engineer"]):
            topics.extend(["Product Management", "A/B Testing", "Data Analysis", "Agile"])
        elif any(kw in role_lower for kw in ["data analyst", "business analyst", "bi "]):
            topics.extend(["Data Science", "SQL", "Database Management Systems", "Python"])
        elif any(kw in role_lower for kw in ["marketing", "growth"]):
            topics.extend(["Digital Marketing", "Analytics", "Product Management"])
        elif any(kw in role_lower for kw in ["finance", "financial", "accounting"]):
            topics.extend(["Corporate Finance", "Financial Modeling", "Accounting"])
        elif any(kw in role_lower for kw in ["frontend", "ui/ux", "designer"]):
            topics.extend(["Object-Oriented Programming", "Computer Networks", "Data Structures & Algorithms"])
        elif any(kw in role_lower for kw in ["backend", "cloud", "devops", "systems"]):
            topics.extend(["Database Management Systems", "SQL", "Operating Systems", "Computer Networks", "Data Structures & Algorithms", "Python"])
        elif any(kw in role_lower for kw in ["software", "sde", "full stack"]):
            topics.extend(["Data Structures & Algorithms", "Database Management Systems", "SQL", "Operating Systems", "Computer Networks", "Java", "Python"])
        else:
            topics.extend(ROLE_TOPIC_MAP.get(target_role, [
                "Data Structures & Algorithms", "Database Management Systems", "Operating Systems", "SQL", "Computer Networks"
            ]))

        # 2. Add domain topics inferred from candidate profile skills and resume competencies
        all_skills = set()
        if candidate_skills:
            all_skills.update(s.lower() for s in candidate_skills)
        if resume_skills:
            all_skills.update(s.lower() for s in resume_skills)

        for skill in all_skills:
            if any(k in skill for k in ["machine learning", "deep learning", "nlp", "computer vision", "scikit", "pytorch", "tensorflow"]):
                if "Machine Learning" not in topics:
                    topics.insert(0, "Machine Learning")
            if any(k in skill for k in ["python", "pandas", "numpy"]):
                if "Python" not in topics:
                    topics.append("Python")
            if any(k in skill for k in ["sql", "rdbms", "postgres", "mysql"]):
                if "SQL" not in topics and "Database Management Systems" not in topics:
                    topics.append("SQL")
            if any(k in skill for k in ["product", "roadmap", "a/b test"]):
                if "Product Management" not in topics:
                    topics.insert(0, "Product Management")
            if any(k in skill for k in ["finance", "valuation", "accounting"]):
                if "Corporate Finance" not in topics:
                    topics.insert(0, "Corporate Finance")

        # Deduplicate while preserving order
        seen = set()
        final_topics = []
        for t in topics:
            if t not in seen:
                seen.add(t)
                final_topics.append(t)

        return final_topics

    def generate_ai_questions(
        self,
        target_role: str,
        topics: List[str],
        skills: List[str],
        count: int = 5
    ) -> List[Question]:
        """Synthesize customized assessment questions using Microsoft Foundry / Azure OpenAI model."""
        import json
        from openai import AzureOpenAI
        from config.settings import settings

        if settings.AZURE_MOCK_MODE or not settings.AZURE_OPENAI_API_KEY:
            return []

        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        system_prompt = (
            "You are an expert technical interviewer and placement examiner. "
            "Generate rigorous, accurate multiple choice diagnostic questions. "
            "Return valid JSON as an array of question objects."
        )
        user_prompt = (
            f"Generate {count} unique multiple-choice questions for candidate preparing for: '{target_role}'.\n"
            f"Focus on topics: {', '.join(topics)}.\n"
            f"Candidate Skills: {', '.join(skills) if skills else 'General'}.\n\n"
            "Return ONLY a JSON array of objects with schema:\n"
            "[\n"
            "  {\n"
            "    \"topic\": \"topic name\",\n"
            "    \"subtopic\": \"subtopic name\",\n"
            "    \"question_text\": \"Question text?\",\n"
            "    \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
            "    \"correct_option_index\": 0,\n"
            "    \"explanation\": \"Detailed pedagogical explanation of the correct choice.\",\n"
            "    \"difficulty\": \"Medium\"\n"
            "  }\n"
            "]"
        )
        try:
            resp = client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=2500
            )
            content = resp.choices[0].message.content or ""
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            raw_qs = json.loads(content.strip())
            created_qs = []
            for item in raw_qs:
                if len(item.get("options", [])) == 4 and "correct_option_index" in item:
                    q = Question(
                        topic=item.get("topic", topics[0] if topics else "Technical"),
                        subtopic=item.get("subtopic", target_role),
                        question_text=item.get("question_text"),
                        options=item.get("options"),
                        correct_option_index=int(item.get("correct_option_index", 0)),
                        explanation=item.get("explanation", ""),
                        difficulty=item.get("difficulty", "Medium")
                    )
                    self.session.add(q)
                    self.session.flush()
                    created_qs.append(q)
            self.session.commit()
            return created_qs
        except Exception:
            return []

    def create_diagnostic_assessment(
        self,
        target_role: str,
        total_questions: int = 10,
        candidate_skills: Optional[List[str]] = None,
        resume_skills: Optional[List[str]] = None,
        use_ai_generation: bool = False
    ) -> Assessment:
        """Generate a role-tailored diagnostic quiz sampling from relevant domain topics and candidate skills."""
        topics = self.resolve_topics_for_role_and_skills(target_role, candidate_skills, resume_skills)
        
        ai_questions = []
        if use_ai_generation:
            combined_skills = list(set((candidate_skills or []) + (resume_skills or [])))
            ai_questions = self.generate_ai_questions(target_role, topics, combined_skills, count=total_questions)

        if len(ai_questions) >= total_questions:
            sampled_questions = ai_questions[:total_questions]
        else:
            sampled_questions = list(ai_questions)
            remaining = total_questions - len(sampled_questions)
            sampled_from_bank = self.question_repo.sample_questions_for_role(topics, total_count=remaining)
            sampled_questions.extend(sampled_from_bank)

        assessment = Assessment(
            title=f"Diagnostic Placement Assessment - {target_role}",
            target_role=target_role,
            topic=", ".join(topics[:3]),
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

    def record_submission(self, submission: AssessmentSubmission) -> AssessmentAttempt:
        """Evaluate submission and persist AssessmentAttempt and AssessmentAnswer records."""
        assessment = self.get_assessment(submission.assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {submission.assessment_id} not found.")

        q_map: Dict[int, Question] = {q.id: q for q in assessment.questions}
        
        total_correct = 0
        topic_stats: Dict[str, Dict[str, int]] = {}
        recorded_answers = []

        for ans in submission.answers:
            q = q_map.get(ans.question_id)
            if not q:
                continue

            if q.topic not in topic_stats:
                topic_stats[q.topic] = {"correct": 0, "total": 0}
            topic_stats[q.topic]["total"] += 1

            is_correct = (ans.selected_option_index == q.correct_option_index)
            if is_correct:
                total_correct += 1
                topic_stats[q.topic]["correct"] += 1

            recorded_answers.append(AssessmentAnswer(
                question_id=q.id,
                selected_option_index=ans.selected_option_index,
                is_correct=is_correct
            ))

        total_questions = len(assessment.questions) or 1
        score_pct = round((total_correct / total_questions) * 100, 2)

        topic_breakdown = [
            {
                "topic": t,
                "correct": stats["correct"],
                "total": stats["total"],
                "percentage": round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0.0
            }
            for t, stats in topic_stats.items()
        ]

        attempt = AssessmentAttempt(
            profile_id=submission.profile_id,
            assessment_id=assessment.id,
            total_questions=total_questions,
            total_correct=total_correct,
            score_percentage=score_pct,
            topic_scores=topic_breakdown,
            answers=recorded_answers
        )

        return self.attempt_repo.create(attempt)

    def evaluate_submission(self, submission: AssessmentSubmission, attempt_id: int = 1) -> AssessmentResultResponse:
        """Evaluate student answers in-memory and return structured result response."""
        assessment = self.get_assessment(submission.assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {submission.assessment_id} not found.")

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

