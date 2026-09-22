from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session

from database.models.student import StudentProfile
from database.models.resume import Resume, JobDescription
from database.models.assessment_attempt import AssessmentAttempt
from database.models.skill_gap import SkillGap
from database.repositories.skill_gap_repository import SkillGapRepository
from schemas.skill_gap_schema import SkillGapReport, PriorityTopicItem


from database.database import SessionLocal


class SkillGapService:
    """Service computing deterministic skill gaps and readiness indices."""

    def __init__(self, session: Optional[Session] = None):
        self._owns_session = session is None
        self.session = session if session is not None else SessionLocal()
        self.gap_repo = SkillGapRepository(self.session)

    def analyze_and_persist_gaps(
        self,
        profile: StudentProfile,
        resume: Optional[Resume] = None,
        jd: Optional[JobDescription] = None,
        latest_attempt: Optional[AssessmentAttempt] = None
    ) -> SkillGap:
        """
        Triangulate candidate profile, parsed resume, targeted JD, and assessment telemetry.
        Persist and return the resulting SkillGap entity.
        """
        # 1. Collect all candidate known skills (case-insensitive)
        candidate_skills: Set[str] = set(s.title() for s in (profile.primary_skills or []))
        if resume and resume.extracted_skills:
            candidate_skills.update(s.title() for s in resume.extracted_skills)

        # 2. Collect JD requirements
        jd_required: Set[str] = set(s.title() for s in (jd.required_skills if jd else []))
        jd_preferred: Set[str] = set(s.title() for s in (jd.preferred_skills if jd else []))

        # Default standard skills if no JD is uploaded
        if not jd_required:
            jd_required = {"Data Structures & Algorithms", "Database Management Systems", "Sql", "Operating Systems"}

        # 3. Analyze assessment topic scores
        topic_scores: Dict[str, float] = {}
        if latest_attempt and latest_attempt.topic_scores:
            for item in latest_attempt.topic_scores:
                t = item.get("topic")
                p = item.get("percentage", 0.0)
                if t:
                    topic_scores[t] = p

        # 4. Compute Missing Skills (in JD required but not in candidate skills)
        cand_lower = {s.lower() for s in candidate_skills}
        missing_skills = [s for s in jd_required if s.lower() not in cand_lower]

        # 5. Compute Weak Skills (scored < 60% in diagnostic assessment)
        weak_skills = []
        for topic, pct in topic_scores.items():
            if pct < 60.0:
                weak_skills.append(f"{topic} ({pct}%)")

        # 6. Compute Strong Skills (scored >= 70% or validated in both profile and test)
        strong_skills = []
        for topic, pct in topic_scores.items():
            if pct >= 70.0:
                strong_skills.append(f"{topic} ({pct}%)")
        
        # Add candidate skills that match JD and are not weak
        for s in candidate_skills:
            if s in jd_required and not any(s.lower() in w.lower() for w in weak_skills):
                if s not in strong_skills:
                    strong_skills.append(s)

        # 7. Generate Prioritized Learning Topics
        priority_topics: List[Dict[str, str]] = []

        # High Priority: Low assessment scores and missing mandatory skills
        for w in weak_skills:
            topic_name = w.split(" (")[0]
            priority_topics.append({
                "topic": topic_name,
                "urgency": "High",
                "rationale": f"Diagnostic assessment showed weakness with score {w.split('(')[-1].rstrip(')')}."
            })

        for m in missing_skills[:4]:
            if not any(p["topic"].lower() == m.lower() for p in priority_topics):
                priority_topics.append({
                    "topic": m,
                    "urgency": "High",
                    "rationale": "Mandatory requirement listed in target job description but absent from resume."
                })

        # Medium Priority: Preferred skills
        for pref in list(jd_preferred)[:3]:
            if pref.lower() not in cand_lower and not any(p["topic"].lower() == pref.lower() for p in priority_topics):
                priority_topics.append({
                    "topic": pref,
                    "urgency": "Medium",
                    "rationale": "Preferred bonus competency that differentiates top candidates."
                })

        # 8. Compute Overall Placement Readiness Score (0 - 100%)
        quiz_factor = latest_attempt.score_percentage if latest_attempt else 50.0
        coverage_ratio = max(0.0, 1.0 - (len(missing_skills) / max(len(jd_required), 1)))
        coverage_factor = coverage_ratio * 100.0
        
        readiness_score = round((0.55 * quiz_factor) + (0.35 * coverage_factor) + 10.0, 2)
        readiness_score = max(5.0, min(98.0, readiness_score))

        skill_gap = SkillGap(
            profile_id=profile.id,
            strong_skills=strong_skills,
            weak_skills=weak_skills,
            missing_skills=missing_skills,
            priority_topics=priority_topics,
            overall_readiness_score=readiness_score
        )

        return self.gap_repo.create(skill_gap)

    def get_latest_gap_report(self, profile_id: int) -> Optional[SkillGap]:
        """Fetch the latest computed skill gap entity for a student."""
        return self.gap_repo.get_latest_for_profile(profile_id)
