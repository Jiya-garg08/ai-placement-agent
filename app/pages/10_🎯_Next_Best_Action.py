import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from agents.recommendation_agent.recommendation_agent import NextActionRecommendationAgent
from services.next_action_service import NextActionService
from database.database import SessionLocal
from database.models.recommendation import NextBestAction

st.set_page_config(
    page_title="Next Best Action | AI Placement Agent",
    page_icon="🎯",
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
            <h1 style="margin: 0; font-size: 2rem;">🎯 Next Best Action Engine</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Dynamic, empirical next best actions guiding your daily placement study session toward highest yield.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Target: {profile['target_role'] if profile else 'SDE'}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

db = SessionLocal()
try:
    rec_agent = NextActionRecommendationAgent(action_service=NextActionService(session=db))
    rec_response = rec_agent.get_recommendations(student_id)

    # 1. Strategic Coach Banner
    st.markdown(
        f"""
        <div class="kpi-card" style="padding: 1.5rem; margin-bottom: 1.5rem; border-left: 4px solid #6366f1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: 700; font-size: 1.15rem; color: #f8fafc;">
                    🧭 Strategic Placement Coaching Memo
                </span>
                <span style="font-size: 0.8rem; background: rgba(99,102,241,0.2); color: #a5b4fc; padding: 0.2rem 0.6rem; border-radius: 4px;">
                    Readiness: {rec_response.overall_readiness_index:.1f}%
                </span>
            </div>
            <div style="font-size: 0.92rem; color: #cbd5e1; line-height: 1.5;">
                {rec_response.motivational_summary}
            </div>
            <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #94a3b8;">
                Primary Bottleneck Target: <b style="color: #f87171;">{rec_response.primary_weakness}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_btn, _ = st.columns([0.3, 0.7])
    with col_btn:
        if st.button("🔄 Refresh / Re-evaluate Actions", use_container_width=True):
            next_action_svc = NextActionService(session=db)
            next_action_svc.generate_next_actions(student_id)
            st.toast("Next actions re-evaluated!", icon="✅")
            st.rerun()

    # 2. Priority Action Cards
    st.markdown("### ⚡ Active Tactical Recommendations")

    page_map = {
        "Practice": "pages/8_💻_Practice.py",
        "Assessments": "pages/4_📝_Diagnostic_Assessment.py",
        "Tutor": "pages/7_🤖_RAG_Tutor.py",
        "Roadmap": "pages/6_📅_Learning_Plan.py"
    }

    actions = rec_response.actions
    if not actions:
        st.success("🎉 You are fully caught up! All tactical placement milestones for today have been achieved.")
    else:
        for act in actions:
            prio = act.priority.lower()
            prio_badge = f"badge-{prio}"
            prio_card = f"priority-{prio}"

            col_c, col_act = st.columns([0.8, 0.2])

            with col_c:
                st.markdown(
                    f"""
                    <div class="action-card {prio_card}">
                        <div class="action-header">
                            <span class="action-title">{act.title}</span>
                            <span class="action-badge {prio_badge}">{act.priority} PRIORITY</span>
                        </div>
                        <div class="action-desc">{act.description}</div>
                        <div class="action-meta">
                            <span>⏱️ <b>{act.estimated_minutes} Minutes</b></span>
                            <span>🏷️ Domain: <b>{act.topic}</b></span>
                            <span>💡 <i>{act.reasoning}</i></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_act:
                st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
                target_page_file = page_map.get(act.target_page, "pages/8_💻_Practice.py")
                if st.button("Execute Action →", key=f"rec_run_{act.id}", use_container_width=True, type="primary"):
                    try:
                        st.switch_page(target_page_file)
                    except Exception:
                        st.info(f"Opening module: {act.target_page}")

                if st.button("Mark Complete ✓", key=f"rec_done_{act.id}", use_container_width=True):
                    next_action_svc = NextActionService(session=db)
                    next_action_svc.mark_action_completed(act.id)
                    st.toast("Action marked as completed!", icon="🎉")
                    st.rerun()

    # 3. Completed Actions Log
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("📜 Historical Completed Actions Log"):
        completed_records = (
            db.query(NextBestAction)
            .filter_by(student_id=student_id, is_completed=True)
            .order_by(NextBestAction.completed_at.desc())
            .limit(10)
            .all()
        )
        if completed_records:
            for cr in completed_records:
                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255,255,255,0.06); padding: 0.6rem 0.9rem; border-radius: 6px; margin-bottom: 0.4rem; display: flex; justify-content: space-between;">
                        <span>✅ <b>{cr.title}</b> ({cr.topic})</span>
                        <span style="font-size: 0.8rem; color: #64748b;">Completed: {cr.completed_at.strftime('%b %d, %Y - %H:%M') if cr.completed_at else 'Done'}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.write("No completed action history yet.")

finally:
    db.close()
