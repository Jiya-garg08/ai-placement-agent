import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from services.analytics_service import AnalyticsService
from services.next_action_service import NextActionService
from database.database import SessionLocal
from database.models.learning_plan import LearningPlan, LearningPlanItem
from database.models.assessment_attempt import AssessmentAttempt

# Page configuration
st.set_page_config(
    page_title="Placement Dashboard | AI Placement Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render persistent sidebar
render_sidebar()

student_id = st.session_state.get("student_id", 1)
profile = get_student_profile_data(student_id)

if not profile:
    st.error("No candidate profile selected. Please select or seed a candidate in the sidebar.")
    st.stop()

# Header
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem;">📊 Placement Readiness Dashboard</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Candidate: <b style="color: #f8fafc;">{profile['name']}</b> &nbsp;|&nbsp; 
                Role: <b style="color: #818cf8;">{profile['target_role']}</b> &nbsp;|&nbsp; 
                Tier Target: <b style="color: #38bdf8;">{profile['target_company_tier']}</b>
            </p>
        </div>
        <div style="font-size: 0.8rem; color: #64748b;">
            Live Telemetry Sync: {datetime.now().strftime('%b %d, %Y - %H:%M UTC')}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch live analytics
db = SessionLocal()
try:
    analytics = AnalyticsService(session=db)
    masteries = analytics.get_topic_mastery_breakdown(student_id)
    velocity = analytics.calculate_learning_velocity(student_id)
    radar_data = analytics.get_radar_chart_data(masteries)
    readiness_idx = analytics.compute_placement_readiness_index(masteries, profile["target_role"])

    next_action_svc = NextActionService(session=db, analytics_service=analytics)
    actions = next_action_svc.get_saved_actions(student_id)
    if not actions:
        # Generate fresh actions if none saved
        action_items = next_action_svc.generate_next_actions(student_id)
        actions = next_action_svc.get_saved_actions(student_id)

    # Fetch active learning plan
    active_plan = db.query(LearningPlan).filter_by(profile_id=student_id, is_active=True).first()
    plan_items = []
    if active_plan:
        plan_items = db.query(LearningPlanItem).filter_by(plan_id=active_plan.id).order_by(LearningPlanItem.week_number.asc()).all()

    # Diagnostic stats
    diag_attempts = db.query(AssessmentAttempt).filter_by(profile_id=student_id).all()
    avg_diag_score = (sum(d.score_percentage for d in diag_attempts) / len(diag_attempts)) if diag_attempts else 0.0

finally:
    db.close()

# ------------------------------------------------------------------------------
# 1. Top Key Performance Indicators (KPIs)
# ------------------------------------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    readiness_status = "Offer Ready" if readiness_idx >= 75 else ("Developing" if readiness_idx >= 50 else "Needs Work")
    st.metric(
        label="Placement Readiness Index",
        value=f"{readiness_idx:.1f}%",
        delta=readiness_status,
        delta_color="normal" if readiness_idx >= 70 else "off"
    )

with kpi_col2:
    st.metric(
        label="Active Preparation Streak",
        value=f"🔥 {velocity.streak_days} Days",
        delta=f"Velocity: {velocity.problems_per_day} probs/day ({velocity.trend})"
    )

with kpi_col3:
    st.metric(
        label="Diagnostic Benchmark",
        value=f"{avg_diag_score:.1f}%",
        delta=f"{len(diag_attempts)} Exam(s) Taken"
    )

with kpi_col4:
    total_solved = profile.get("total_questions_solved", 0)
    st.metric(
        label="Practice Drill Questions",
        value=f"{total_solved} Solved",
        delta=f"{velocity.hours_per_week} hrs/week logged"
    )

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Domain Competency & Radar Chart
# ------------------------------------------------------------------------------
st.markdown("### 🕸️ Multi-Domain Competency & Benchmark Radar")

col_radar, col_breakdown = st.columns([1.1, 0.9])

with col_radar:
    # Build Plotly Radar / Spider Chart
    categories = list(radar_data.keys())
    values = list(radar_data.values())
    
    # Close the polygon by repeating first item
    categories_closed = categories + [categories[0]] if categories else []
    values_closed = values + [values[0]] if values else []
    benchmark_closed = [80.0] * len(categories_closed)  # Tier 1 Benchmark target 80%

    fig = go.Figure()

    # Candidate mastery trace
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        name=f"{profile['name']} (Actual)",
        line=dict(color='#6366f1', width=2),
        fillcolor='rgba(99, 102, 241, 0.3)'
    ))

    # Tier 1 Benchmark trace
    fig.add_trace(go.Scatterpolar(
        r=benchmark_closed,
        theta=categories_closed,
        mode='lines',
        name="Tier 1 Role Benchmark (80%)",
        line=dict(color='#38bdf8', width=1.5, dash='dash')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(size=9, color="#94a3b8"),
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#f1f5f9"),
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            bgcolor="rgba(15, 23, 42, 0.6)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#cbd5e1", size=11)
        ),
        margin=dict(l=40, r=40, t=20, b=50),
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)

with col_breakdown:
    st.markdown("#### 🎯 Domain Mastery Status")
    
    # Group masteries by level
    level_colors = {
        "Mastered": "#10b981",
        "Competent": "#38bdf8",
        "Developing": "#f59e0b",
        "Novice": "#ef4444"
    }

    # Show mastery breakdown scrollable list
    for item in masteries[:7]:
        color = level_colors.get(item.level, "#94a3b8")
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <span style="font-size: 0.88rem; font-weight: 500; color: #f1f5f9;">{item.topic}</span>
                <span style="font-size: 0.75rem; font-weight: 600; color: {color}; background: rgba(255,255,255,0.06); padding: 0.15rem 0.5rem; border-radius: 4px;">
                    {item.level} ({item.mastery_percentage:.0f}%)
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.progress(min(item.mastery_percentage / 100.0, 1.0))

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. 4-Week Adaptive Roadmap Progress
# ------------------------------------------------------------------------------
st.markdown("### 📅 Adaptive Learning Roadmap Status")

if active_plan and plan_items:
    completed_count = sum(1 for item in plan_items if item.status == "Completed")
    progress_val = completed_count / len(plan_items)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 0.95rem; font-weight: 600; color: #f8fafc;">{active_plan.plan_name}</span>
            <span style="font-size: 0.85rem; color: #818cf8;">{completed_count} of {len(plan_items)} Milestones Complete ({progress_val * 100:.0f}%)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(progress_val)

    plan_cols = st.columns(4)
    status_emoji = {
        "Completed": "✅",
        "In Progress": "🔄",
        "Pending": "⏳"
    }

    for i, item in enumerate(plan_items[:4]):
        with plan_cols[i]:
            card_class = "completed" if item.status == "Completed" else ("in-progress" if item.status == "In Progress" else "pending")
            st.markdown(
                f"""
                <div class="roadmap-step {card_class}">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                        <span>WEEK {item.week_number}</span>
                        <span>{status_emoji.get(item.status, '')} {item.status}</span>
                    </div>
                    <div style="font-weight: 600; font-size: 0.92rem; color: #f8fafc; margin: 0.4rem 0;">
                        {item.topic[:28]}
                    </div>
                    <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.3;">
                        {item.learning_objectives[:75]}...
                    </div>
                    <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.5rem;">
                        Target: {item.practice_goal_count} practice drills
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No active learning roadmap generated yet. Complete the Diagnostic Exam to generate your 4-week personalized plan.")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. Top 3 Next Best Actions
# ------------------------------------------------------------------------------
st.markdown("### 🎯 Top Prioritized Next Best Actions")
st.markdown("AI-surfaced tactical actions calibrated to your primary weak spots:")

page_mapping = {
    "Practice": "pages/8_💻_Practice.py",
    "Assessments": "pages/4_📝_Diagnostic_Assessment.py",
    "Tutor": "pages/7_🤖_RAG_Tutor.py",
    "Roadmap": "pages/6_📅_Learning_Plan.py"
}

uncompleted_actions = [a for a in actions if not a.is_completed]
if not uncompleted_actions:
    st.success("🎉 Outstanding! You have completed all active recommended actions. Regenerating fresh recommendations...")
    db = SessionLocal()
    try:
        next_action_svc = NextActionService(session=db)
        next_action_svc.generate_next_actions(student_id)
        st.rerun()
    finally:
        db.close()
else:
    for idx, act in enumerate(uncompleted_actions[:3]):
        priority_class = f"priority-{act.priority.lower()}"
        badge_class = f"badge-{act.priority.lower()}"

        col_card, col_action = st.columns([0.82, 0.18])

        with col_card:
            st.markdown(
                f"""
                <div class="action-card {priority_class}">
                    <div class="action-header">
                        <span class="action-title">{act.title}</span>
                        <span class="action-badge {badge_class}">{act.priority} PRIORITY</span>
                    </div>
                    <div class="action-desc">{act.description}</div>
                    <div class="action-meta">
                        <span>⏱️ Estimated: <b>{act.estimated_minutes} mins</b></span>
                        <span>🏷️ Topic: <b>{act.topic}</b></span>
                        <span>💡 <i>{getattr(act, 'reasoning', None) or act.action_type or 'Curated recommendation'}</i></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_action:
            st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
            # Navigation trigger
            target_file = page_mapping.get(act.target_page, "pages/8_💻_Practice.py")
            if st.button(f"Start Action →", key=f"start_{act.id}", use_container_width=True):
                try:
                    st.switch_page(target_file)
                except Exception:
                    st.info(f"Target module '{act.target_page}' is queued for Phase 12 integration.")

            # Mark done toggle
            if st.button("Mark Done ✓", key=f"done_{act.id}", use_container_width=True):
                db = SessionLocal()
                try:
                    svc = NextActionService(session=db)
                    svc.mark_action_completed(act.id)
                    st.toast("Action marked as completed! Updating dashboard...", icon="🎉")
                    st.rerun()
                finally:
                    db.close()
