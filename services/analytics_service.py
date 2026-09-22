from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models.student import StudentProfile
from database.models.assessment_attempt import AssessmentAttempt, AssessmentAnswer
from database.models.assessment import Question
from database.models.practice import PracticeAttempt, PracticeStreak
from schemas.evaluation_schema import (
    TopicMasteryItem,
    LearningVelocity,
    PlacementReadinessEvaluation
)

CORE_PLACEMENT_DOMAINS = [
    "Data Structures & Algorithms",
    "Database Management Systems",
    "SQL",
    "Operating Systems",
    "Computer Networks",
    "Object-Oriented Programming",
    "Java",
    "Python",
    "Machine Learning",
    "Aptitude"
]

DOMAIN_ACRONYMS = {
    "Data Structures & Algorithms": "DSA",
    "Database Management Systems": "DBMS",
    "SQL": "SQL",
    "Operating Systems": "OS",
    "Computer Networks": "Networks",
    "Object-Oriented Programming": "OOP",
    "Java": "Java",
    "Python": "Python",
    "Machine Learning": "ML",
    "Aptitude": "Aptitude"
}


class AnalyticsService:
    """Mathematical aggregation engine calculating topic masteries, preparation velocity,

    radar chart visualization data, and holistic placement readiness.
    """

    def __init__(self, session: Optional[Session] = None):
        self._owns_session = session is None
        self.session = session if session is not None else SessionLocal()

    def get_topic_mastery_breakdown(self, student_id: int) -> List[TopicMasteryItem]:
        """Aggregate performance telemetry across diagnostic assessments and practice attempts."""
        # 1. Fetch Assessment Answers for student
        assessment_answers = (
            self.session.query(AssessmentAnswer, Question.topic)
            .join(Question, AssessmentAnswer.question_id == Question.id)
            .join(AssessmentAttempt, AssessmentAnswer.attempt_id == AssessmentAttempt.id)
            .filter(AssessmentAttempt.profile_id == student_id)
            .all()
        )

        # 2. Fetch Practice Attempts for student
        practice_attempts = (
            self.session.query(PracticeAttempt)
            .filter(PracticeAttempt.student_id == student_id)
            .all()
        )

        # 3. Aggregate by canonical domain
        domain_stats: Dict[str, Dict[str, Any]] = {
            domain: {
                "diag_total": 0,
                "diag_correct": 0,
                "practice_total": 0,
                "practice_correct": 0
            }
            for domain in CORE_PLACEMENT_DOMAINS
        }

        # Process diagnostic answers
        for ans, topic in assessment_answers:
            matched_domain = self._normalize_domain(topic)
            if matched_domain in domain_stats:
                domain_stats[matched_domain]["diag_total"] += 1
                if ans.is_correct:
                    domain_stats[matched_domain]["diag_correct"] += 1

        # Process practice attempts
        for pa in practice_attempts:
            matched_domain = self._normalize_domain(pa.topic)
            if matched_domain in domain_stats:
                domain_stats[matched_domain]["practice_total"] += 1
                if pa.is_correct:
                    domain_stats[matched_domain]["practice_correct"] += 1

        # 4. Calculate Mastery Percentage and Mastery Level
        mastery_items: List[TopicMasteryItem] = []
        for domain, stats in domain_stats.items():
            total_attempts = stats["diag_total"] + stats["practice_total"]
            total_correct = stats["diag_correct"] + stats["practice_correct"]

            if total_attempts == 0:
                mastery_pct = 0.0
                accuracy_pct = 0.0
            else:
                accuracy_pct = round((total_correct / total_attempts) * 100.0, 1)
                
                # Weighted mastery: 60% diagnostic performance + 40% practice drill consistency
                diag_score = (stats["diag_correct"] / max(stats["diag_total"], 1)) * 100.0 if stats["diag_total"] > 0 else accuracy_pct
                prac_score = (stats["practice_correct"] / max(stats["practice_total"], 1)) * 100.0 if stats["practice_total"] > 0 else accuracy_pct
                
                if stats["diag_total"] > 0 and stats["practice_total"] > 0:
                    mastery_pct = round((diag_score * 0.60) + (prac_score * 0.40), 1)
                else:
                    mastery_pct = accuracy_pct

            # Determine level
            if mastery_pct >= 80.0:
                level = "Mastered"
            elif mastery_pct >= 65.0:
                level = "Competent"
            elif mastery_pct >= 40.0:
                level = "Developing"
            else:
                level = "Novice"

            mastery_items.append(
                TopicMasteryItem(
                    topic=domain,
                    mastery_percentage=mastery_pct,
                    level=level,
                    assessments_taken=stats["diag_total"],
                    practice_problems_solved=stats["practice_total"],
                    accuracy_rate=accuracy_pct
                )
            )

        return mastery_items

    def get_radar_chart_data(self, topic_masteries: List[TopicMasteryItem]) -> Dict[str, float]:
        """Format mastery percentages for radar / spider chart visualization."""
        radar_data = {}
        for item in topic_masteries:
            short_name = DOMAIN_ACRONYMS.get(item.topic, item.topic)
            radar_data[short_name] = item.mastery_percentage
        return radar_data

    def calculate_learning_velocity(self, student_id: int) -> LearningVelocity:
        """Compute preparation velocity (problems/day, hours/week) and momentum trend."""
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        # Recent attempts (last 7 days)
        recent_practice = (
            self.session.query(PracticeAttempt)
            .filter(PracticeAttempt.student_id == student_id, PracticeAttempt.created_at >= seven_days_ago)
            .all()
        )
        recent_diag = (
            self.session.query(AssessmentAttempt)
            .filter(AssessmentAttempt.profile_id == student_id, AssessmentAttempt.created_at >= seven_days_ago)
            .all()
        )

        # Prior attempts (days 8 to 14)
        prior_practice_count = (
            self.session.query(PracticeAttempt)
            .filter(
                PracticeAttempt.student_id == student_id,
                PracticeAttempt.created_at >= fourteen_days_ago,
                PracticeAttempt.created_at < seven_days_ago
            )
            .count()
        )

        recent_count = len(recent_practice) + len(recent_diag)
        problems_per_day = round(recent_count / 7.0, 1)

        total_time_seconds = sum(pa.time_spent_seconds for pa in recent_practice)
        total_time_seconds += len(recent_diag) * 900  # Estimate 15 mins per completed diagnostic test
        hours_per_week = round(total_time_seconds / 3600.0, 1)

        # Calculate momentum trend
        if prior_practice_count == 0:
            trend = "Accelerating" if recent_count > 0 else "Consistent"
        else:
            ratio = recent_count / max(prior_practice_count, 1)
            if ratio >= 1.20:
                trend = "Accelerating"
            elif ratio <= 0.80:
                trend = "Decelerating"
            else:
                trend = "Consistent"

        # Fetch streak
        streak_record = self.session.query(PracticeStreak).filter_by(student_id=student_id).first()
        streak_days = streak_record.current_streak if streak_record else 0

        return LearningVelocity(
            problems_per_day=problems_per_day,
            hours_per_week=hours_per_week,
            trend=trend,
            streak_days=streak_days
        )

    def compute_placement_readiness_index(
        self,
        topic_masteries: List[TopicMasteryItem],
        target_role: Optional[str] = None
    ) -> float:
        """Compute holistic readiness index (0-100%) weighting core role competencies."""
        if not topic_masteries:
            return 0.0

        scores = [item.mastery_percentage for item in topic_masteries if item.assessments_taken + item.practice_problems_solved > 0]
        if not scores:
            return 0.0

        # High priority baseline: average of tested areas, weighted against full curriculum breadth
        active_avg = sum(scores) / len(scores)
        coverage_factor = min(len(scores) / 5.0, 1.0)  # rewarded for testing across at least 5 domains

        readiness = round(active_avg * (0.60 + 0.40 * coverage_factor), 1)
        return min(max(readiness, 0.0), 100.0)

    def _normalize_domain(self, raw_topic: str) -> str:
        """Match varied topic labels to canonical domain categories."""
        if not raw_topic:
            return "General"
        lower = raw_topic.lower().replace("&", "and")

        if any(k in lower for k in ["data structure", "algorithm", "dsa", "binary tree", "graph", "array"]):
            return "Data Structures & Algorithms"
        if any(k in lower for k in ["dbms", "database", "acid", "normalization"]):
            return "Database Management Systems"
        if "sql" in lower or "query" in lower:
            return "SQL"
        if any(k in lower for k in ["operating system", "os", "process", "deadlock", "memory"]):
            return "Operating Systems"
        if any(k in lower for k in ["network", "tcp", "udp", "osi", "ip"]):
            return "Computer Networks"
        if any(k in lower for k in ["oop", "object oriented", "inheritance", "polymorphism"]):
            return "Object-Oriented Programming"
        if "java" in lower:
            return "Java"
        if "python" in lower:
            return "Python"
        if any(k in lower for k in ["machine learning", "ml", "regression", "neural"]):
            return "Machine Learning"
        if any(k in lower for k in ["aptitude", "quantitative", "probability", "permutation"]):
            return "Aptitude"

        return raw_topic
