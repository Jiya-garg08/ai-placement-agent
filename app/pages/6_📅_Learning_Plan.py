import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from agents.planner_agent.planner_agent import LearningPlannerAgent
from database.database import SessionLocal
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.models.skill_gap import SkillGap

st.set_page_config(
    page_title="Learning Roadmap | AI Placement Agent",
    page_icon="📅",
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
            <h1 style="margin: 0; font-size: 2rem;">📅 Adaptive Learning Roadmap</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Personalized 4-week preparation plan dynamically scheduled against your skill gaps and target company tier.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Candidate: {profile['name'] if profile else 'Candidate'}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

db = SessionLocal()
try:
    plan = db.query(LearningPlan).filter_by(profile_id=student_id, is_active=True).first()
    skill_gap = db.query(SkillGap).filter_by(profile_id=student_id).order_by(SkillGap.created_at.desc()).first()

    col_h1, col_h2 = st.columns([0.65, 0.35])
    with col_h2:
        if st.button("✨ Generate / Re-plan Roadmap", use_container_width=True, type="primary"):
            with st.spinner("AI Curriculum Architect synthesizing personalized 4-week roadmap..."):
                planner = LearningPlannerAgent()
                plan_struct = planner.generate_plan(
                    target_role=profile["target_role"] if profile else "Software Development Engineer (SDE)",
                    skill_gap=skill_gap,
                    total_weeks=4,
                    daily_hours=2.5
                )

                # Deactivate older plans
                for old in db.query(LearningPlan).filter_by(profile_id=student_id, is_active=True).all():
                    old.is_active = False

                new_plan = LearningPlan(
                    profile_id=student_id,
                    plan_name=plan_struct.plan_name,
                    target_role=plan_struct.target_role,
                    total_weeks=plan_struct.total_weeks,
                    daily_hours_target=plan_struct.daily_hours_target,
                    is_active=True
                )
                db.add(new_plan)
                db.flush()

                for it in plan_struct.items:
                    item_rec = LearningPlanItem(
                        plan_id=new_plan.id,
                        week_number=it.week_number,
                        order_index=it.order_index,
                        topic=it.topic,
                        subtopics=it.subtopics,
                        priority=it.priority,
                        learning_objectives=it.learning_objectives,
                        practice_goal_count=it.practice_goal_count,
                        status=it.status
                    )
                    db.add(item_rec)

                db.commit()
                st.toast("New personalized preparation roadmap generated!", icon="🎉")
                st.rerun()

    if not plan:
        st.info("No active learning roadmap found. Click 'Generate / Re-plan Roadmap' above to create one.")
        st.stop()

    items = db.query(LearningPlanItem).filter_by(plan_id=plan.id).order_by(LearningPlanItem.week_number.asc()).all()

    # Progress Calculation
    completed = sum(1 for it in items if it.status == "Completed")
    total_items = len(items) or 1
    prog_pct = completed / total_items

    with col_h1:
        st.markdown(
            f"""
            <div style="font-size: 1.15rem; font-weight: 600; color: #f8fafc;">
                {plan.plan_name}
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem;">
                Target: <b>{plan.target_role}</b> &nbsp;|&nbsp; Daily Commitment: <b>{plan.daily_hours_target} hrs/day</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.progress(prog_pct)
    st.caption(f"Roadmap Completion: {completed} of {len(items)} milestones completed ({prog_pct * 100:.0f}%)")

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4-Week Accordion
    status_emoji = {"Completed": "✅", "In Progress": "🔄", "Pending": "⏳"}
    
    for item in items:
        with st.expander(
            f"{status_emoji.get(item.status, '⏳')} Week {item.week_number}: {item.topic} ({item.status})",
            expanded=(item.status == "In Progress")
        ):
            col_info, col_controls = st.columns([0.72, 0.28])
            
            with col_info:
                st.markdown(f"**Target Practice Goal:** `{item.practice_goal_count} Problems` &nbsp;|&nbsp; **Priority:** `{item.priority}`")
                st.markdown(f"**Learning Objectives:** {item.learning_objectives}")
                
                if item.subtopics:
                    st.markdown("##### 📌 Key Subtopics & Checklist:")
                    for sub in item.subtopics:
                        st.markdown(f"- [ ] {sub}")

            with col_controls:
                st.markdown("##### 🔄 Milestone Status")
                current_st = item.status
                STATUS_CYCLE = ["Pending", "In Progress", "Completed"]
                next_status = STATUS_CYCLE[(STATUS_CYCLE.index(current_st) + 1) % len(STATUS_CYCLE)] if current_st in STATUS_CYCLE else "Completed"
                
                if st.button(f"Move to '{next_status}'", key=f"cycle_{item.id}", use_container_width=True):
                    item.status = next_status
                    db.commit()
                    st.toast(f"Milestone updated to {next_status}!", icon="✅")
                    st.rerun()

                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                if st.button("Practice This Topic →", key=f"prac_{item.id}", use_container_width=True):
                    st.switch_page("pages/8_💻_Practice.py")

finally:
    db.close()
