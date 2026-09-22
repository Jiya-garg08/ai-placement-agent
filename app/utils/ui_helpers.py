import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import streamlit as st
from sqlalchemy.orm import Session

from database.database import SessionLocal, init_db
from database.models.student import User, StudentProfile
from database.models.practice import PracticeStreak
from database.models.skill_gap import SkillGap
from app.utils.seed_demo_student import seed_demo_candidate
from services.analytics_service import AnalyticsService


def load_custom_css() -> None:
    """Inject custom CSS stylesheet into Streamlit application."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def ensure_seed_data() -> int:
    """Ensure database has demo candidate profile; seed if absent."""
    init_db()
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter_by(email="jiya.garg@example.com").first()
        if user and user.profile:
            # Ensure next actions exist
            next_action_svc = NextActionService(session=db)
            saved = next_action_svc.get_saved_actions(user.profile.id)
            if not saved:
                next_action_svc.generate_next_actions(user.profile.id)
            return user.profile.id

        demo_profile = seed_demo_candidate(session=db)
        return demo_profile.id
    finally:
        db.close()


def list_all_students() -> List[Dict[str, Any]]:
    """List all registered candidate profiles with user details for sidebar switching."""
    db: Session = SessionLocal()
    try:
        profiles = (
            db.query(StudentProfile, User)
            .join(User, StudentProfile.user_id == User.id)
            .order_by(StudentProfile.id.asc())
            .all()
        )
        candidates = []
        for prof, usr in profiles:
            candidates.append({
                "id": prof.id,
                "user_id": usr.id,
                "name": usr.name,
                "email": usr.email,
                "target_role": prof.target_role,
                "college": prof.college or "University",
                "grad_year": prof.graduation_year or 2026,
            })
        return candidates
    finally:
        db.close()


def get_student_profile_data(profile_id: int) -> Optional[Dict[str, Any]]:
    """Fetch complete candidate summary dictionary by profile ID."""
    db: Session = SessionLocal()
    try:
        prof = db.query(StudentProfile).filter_by(id=profile_id).first()
        if not prof:
            return None
        usr = db.query(User).filter_by(id=prof.user_id).first()
        streak = db.query(PracticeStreak).filter_by(student_id=prof.id).first()
        gap = (
            db.query(SkillGap)
            .filter_by(profile_id=prof.id)
            .order_by(SkillGap.created_at.desc())
            .first()
        )

        analytics = AnalyticsService(session=db)
        mastery = analytics.get_topic_mastery_breakdown(prof.id)
        readiness = analytics.compute_placement_readiness_index(mastery, prof.target_role)

        return {
            "id": prof.id,
            "user_id": usr.id if usr else 0,
            "name": usr.name if usr else "Candidate",
            "email": usr.email if usr else "",
            "target_role": prof.target_role,
            "career_goal": prof.career_goal or "Placement Preparation",
            "target_company_tier": prof.target_company_tier or "Tier 1",
            "college": prof.college or "University",
            "graduation_year": prof.graduation_year or 2026,
            "current_semester": prof.current_semester or 7,
            "primary_skills": prof.primary_skills or [],
            "current_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
            "total_questions_solved": streak.total_questions_solved if streak else 0,
            "readiness_score": readiness if readiness > 0 else (gap.overall_readiness_score if gap else 65.0),
            "strong_skills": gap.strong_skills if gap else [],
            "weak_skills": gap.weak_skills if gap else [],
            "missing_skills": gap.missing_skills if gap else []
        }
    finally:
        db.close()


def initialize_session_state() -> None:
    """Initialize foundational Streamlit session state keys if not already set."""
    if "student_id" not in st.session_state:
        default_id = ensure_seed_data()
        st.session_state["student_id"] = default_id

    # Load fresh profile data
    profile_data = get_student_profile_data(st.session_state["student_id"])
    if profile_data:
        st.session_state["student_name"] = profile_data["name"]
        st.session_state["student_email"] = profile_data["email"]
        st.session_state["target_role"] = profile_data["target_role"]
        st.session_state["current_streak"] = profile_data["current_streak"]
        st.session_state["readiness_score"] = profile_data["readiness_score"]
    else:
        st.session_state["student_name"] = "Candidate"
        st.session_state["student_email"] = "candidate@example.com"
        st.session_state["target_role"] = "Software Development Engineer"
        st.session_state["current_streak"] = 0
        st.session_state["readiness_score"] = 50.0

    if "azure_mock_mode" not in st.session_state:
        st.session_state["azure_mock_mode"] = True
    if "budget_spent" not in st.session_state:
        st.session_state["budget_spent"] = 0.00
    if "budget_grant" not in st.session_state:
        st.session_state["budget_grant"] = 200.00


def render_kpi_card(title: str, value: str, delta: Optional[str] = None, delta_type: str = "positive") -> str:
    """Generate HTML string for a modern glassmorphic KPI card."""
    delta_class = f"delta-{delta_type}"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
