import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
import plotly.graph_objects as go
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from agents.evaluation_agent.evaluation_agent import PerformanceEvaluationAgent
from database.database import SessionLocal

st.set_page_config(
    page_title="Performance Analytics | AI Placement Agent",
    page_icon="📈",
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
            <h1 style="margin: 0; font-size: 2rem;">📈 Performance Analytics & Hiring Critique</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Holistic performance evaluation synthesizing quantitative test telemetry into hiring manager appraisals.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Evaluation Engine: Online</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

db = SessionLocal()
try:
    eval_agent = PerformanceEvaluationAgent()
    evaluation = eval_agent.evaluate_student(student_id, session=db)

    # 1. Top Metrics Banner
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.metric(
            label="Placement Readiness",
            value=f"{evaluation.overall_readiness_index:.1f}%",
            delta=evaluation.readiness_tier
        )
    with col_k2:
        st.metric(
            label="Preparation Velocity",
            value=f"{evaluation.learning_velocity.problems_per_day} probs/day",
            delta=f"Trend: {evaluation.learning_velocity.trend}"
        )
    with col_k3:
        st.metric(
            label="Study Commitment",
            value=f"{evaluation.learning_velocity.hours_per_week} hrs/week",
            delta=f"🔥 {evaluation.learning_velocity.streak_days}-Day Streak"
        )
    with col_k4:
        st.metric(
            label="Readiness Milestone",
            value=evaluation.readiness_tier,
            delta="Placement Season 2026"
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 2. Radar Chart and Technical Appraisal
    col_radar, col_critique = st.columns([1.1, 0.9])

    with col_radar:
        st.markdown("#### 🕸️ Multi-Domain Competency Radar")
        radar_data = evaluation.radar_chart_data
        categories = list(radar_data.keys())
        values = list(radar_data.values())

        cat_closed = categories + [categories[0]] if categories else []
        val_closed = values + [values[0]] if values else []
        bench_closed = [80.0] * len(cat_closed)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=val_closed,
            theta=cat_closed,
            fill='toself',
            name=f"{profile['name'] if profile else 'Candidate'}",
            line=dict(color='#6366f1', width=2),
            fillcolor='rgba(99, 102, 241, 0.3)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=bench_closed,
            theta=cat_closed,
            mode='lines',
            name="Tier 1 Benchmark (80%)",
            line=dict(color='#38bdf8', width=1.5, dash='dash')
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="#94a3b8", size=9)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="#f8fafc", size=10)),
                bgcolor="rgba(15, 23, 42, 0.6)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(color="#cbd5e1", size=11)),
            margin=dict(l=30, r=30, t=20, b=40),
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_critique:
        st.markdown("#### 👔 Technical Hiring Manager Appraisal")
        st.markdown(
            f"""
            <div class="kpi-card" style="padding: 1.2rem; min-height: 330px;">
                <div style="font-size: 0.92rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 0.8rem;">
                    {evaluation.qualitative_evaluation_summary}
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.8rem; margin-top: 0.8rem;">
                    <b style="color: #f8fafc; font-size: 0.88rem;">Recommended Tactical Focus:</b>
            """,
            unsafe_allow_html=True
        )
        for fa in evaluation.recommended_focus_areas:
            st.markdown(f"- 🎯 {fa}")
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Comprehensive Domain Mastery Table
    st.markdown("### 📊 Comprehensive Domain Telemetry Breakdown")
    
    table_rows = []
    for tm in evaluation.topic_masteries:
        table_rows.append({
            "Topic Domain": tm.topic,
            "Mastery Level": tm.level,
            "Mastery Score": f"{tm.mastery_percentage:.1f}%",
            "Accuracy": f"{tm.accuracy_rate:.1f}%",
            "Diagnostic Exams": tm.assessments_taken,
            "Practice Problems": tm.practice_problems_solved
        })

    st.dataframe(
        table_rows,
        column_config={
            "Topic Domain": st.column_config.TextColumn("Curriculum Domain", width="large"),
            "Mastery Level": st.column_config.TextColumn("Tier Level", width="medium"),
            "Mastery Score": st.column_config.TextColumn("Mastery %", width="small"),
            "Accuracy": st.column_config.TextColumn("Accuracy Rate", width="small"),
            "Diagnostic Exams": st.column_config.NumberColumn("Diagnostic Tests", width="small"),
            "Practice Problems": st.column_config.NumberColumn("Practice Drills", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )

finally:
    db.close()
