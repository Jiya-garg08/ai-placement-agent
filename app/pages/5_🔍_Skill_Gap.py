import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from services.skill_gap_service import SkillGapService
from database.database import SessionLocal
from database.models.student import StudentProfile
from database.models.skill_gap import SkillGap
from database.models.assessment_attempt import AssessmentAttempt

st.set_page_config(
    page_title="Skill Gap Matrix | AI Placement Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

student_id = st.session_state.get("student_id", 1)
profile = get_student_profile_data(student_id)

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem;">🔍 Triangulated Skill Gap Engine</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Four-way triangulation across student profile, parsed resume, target JD requirements, and diagnostic telemetry.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Target Role: {profile['target_role'] if profile else 'SDE'}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

db = SessionLocal()
try:
    svc = SkillGapService(session=db)
    gap_record = svc.get_latest_gap_report(student_id)

    col_btn1, col_btn2 = st.columns([0.3, 0.7])
    with col_btn1:
        if st.button("🔄 Re-Calculate Skill Gap", use_container_width=True, type="primary"):
            with st.spinner("Triangulating profile skills against latest test telemetry..."):
                prof_model = db.query(StudentProfile).filter_by(id=student_id).first()
                latest_attempt = db.query(AssessmentAttempt).filter_by(profile_id=student_id).order_by(AssessmentAttempt.created_at.desc()).first()
                if prof_model:
                    gap_record = svc.analyze_and_persist_gaps(profile=prof_model, latest_attempt=latest_attempt)
                    st.toast("Skill gap matrix re-calculated!", icon="✅")
                    st.rerun()

    if not gap_record:
        st.info("No skill gap record found. Click 'Re-Calculate Skill Gap' above or complete a Diagnostic Assessment.")
        st.stop()

    readiness = gap_record.overall_readiness_score
    r_color = "#10b981" if readiness >= 75 else ("#f59e0b" if readiness >= 50 else "#ef4444")

    # Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Readiness Score", f"{readiness:.1f}%", delta="Placement Calibrated")
    with kpi2:
        st.metric("Strong Skills", len(gap_record.strong_skills or []))
    with kpi3:
        st.metric("Weak Areas", len(gap_record.weak_skills or []))
    with kpi4:
        st.metric("Missing Requirements", len(gap_record.missing_skills or []))

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Triangulation Grid
    st.markdown("### 🧩 Competency Triangulation Grid")
    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 1.2rem; min-height: 280px;">
                <h4 style="color: #34d399; margin-top: 0;">🟢 Strong Competencies</h4>
                <p style="font-size: 0.82rem; color: #94a3b8;">Skills verified in profile & tests (>= 70% accuracy):</p>
            """,
            unsafe_allow_html=True
        )
        if gap_record.strong_skills:
            for s in gap_record.strong_skills:
                st.markdown(f"- ✅ **{s}**")
        else:
            st.write("No strong skills logged.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 1.2rem; min-height: 280px;">
                <h4 style="color: #fbbf24; margin-top: 0;">🟡 Weak Competencies</h4>
                <p style="font-size: 0.82rem; color: #94a3b8;">Areas with diagnostic accuracy < 60%:</p>
            """,
            unsafe_allow_html=True
        )
        if gap_record.weak_skills:
            for w in gap_record.weak_skills:
                st.markdown(f"- ⚠️ **{w}**")
        else:
            st.write("No critical weak areas detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g3:
        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 1.2rem; min-height: 280px;">
                <h4 style="color: #f87171; margin-top: 0;">🔴 Missing Requirements</h4>
                <p style="font-size: 0.82rem; color: #94a3b8;">Mandatory role skills absent from profile:</p>
            """,
            unsafe_allow_html=True
        )
        if gap_record.missing_skills:
            for m in gap_record.missing_skills:
                st.markdown(f"- ❌ **{m}**")
        else:
            st.write("All target JD requirements present!")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Priority Learning Topics
    st.markdown("### 🎯 Prioritized Remediation Roadmap")
    if gap_record.priority_topics:
        for idx, pt in enumerate(gap_record.priority_topics):
            if isinstance(pt, dict):
                topic_title = pt.get("topic", "Focus Area")
                urgency = pt.get("urgency", "High" if idx == 0 else "Medium")
                rationale = pt.get("rationale", "Identified priority area for your target placement role.")
            else:
                topic_title = str(pt)
                urgency = "High" if idx < 2 else "Medium"
                rationale = f"Core competency in {topic_title} targeted for placement interview readiness."

            u_color = "#ef4444" if urgency.lower() == "high" else "#f59e0b"
            
            st.markdown(
                f"""
                <div class="kpi-card" style="margin-bottom: 0.75rem; padding: 0.9rem 1.2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; font-size: 1rem; color: #f8fafc;">
                            #{idx + 1} {topic_title}
                        </span>
                        <span style="font-size: 0.75rem; font-weight: 700; color: {u_color}; background: rgba(255,255,255,0.06); padding: 0.2rem 0.5rem; border-radius: 4px;">
                            {urgency.upper()} URGENCY
                        </span>
                    </div>
                    <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0.4rem 0 0 0;">
                        {rationale}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("Generate 4-Week Learning Roadmap →", type="primary", use_container_width=True):
            st.switch_page("pages/6_📅_Learning_Plan.py")
    with col_nav2:
        if st.button("Drill Practice Problems on Weak Skills →", use_container_width=True):
            st.switch_page("pages/8_💻_Practice.py")

finally:
    db.close()
