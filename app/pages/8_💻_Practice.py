import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from services.practice_service import PracticeService
from schemas.practice_schema import PracticeSubmissionRequest
from database.database import SessionLocal

st.set_page_config(
    page_title="Interactive Practice Engine | AI Placement Agent",
    page_icon="💻",
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
            <h1 style="margin: 0; font-size: 2rem;">💻 Interactive Practice Engine</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Targeted conceptual MCQ drilling and algorithmic coding challenges with calendar streak gamification.
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
    practice_svc = PracticeService(session=db)
    summary = practice_svc.get_student_practice_summary(student_id)

    # 1. Streak & Gamification KPI Banner
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.metric("Daily Streak", f"🔥 {summary.current_streak} Days", delta=f"Record: {summary.longest_streak} Days")
    with col_k2:
        st.metric("Problems Solved", summary.total_questions_solved, delta="Logged attempts")
    with col_k3:
        st.metric("Overall Accuracy", f"{summary.overall_accuracy:.1f}%", delta=f"{summary.total_correct} Correct")
    with col_k4:
        st.metric("Gamification Points", f"⭐ {summary.total_correct * 10} pts", delta="+10 per solved")

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    tab_mcq, tab_coding = st.tabs(["🎯 Conceptual MCQ Drills", "💻 Algorithmic Coding Challenges"])

    # --------------------------------------------------------------------------
    # TAB 1: Conceptual MCQ Drills
    # --------------------------------------------------------------------------
    with tab_mcq:
        st.markdown("#### 🎯 Domain-Targeted Multiple Choice Drills")
        
        col_flt1, col_flt2 = st.columns([0.6, 0.4])
        with col_flt1:
            DOMAINS = [
                "All Domains", "Data Structures & Algorithms", "Database Management Systems",
                "SQL", "Operating Systems", "Java", "Python", "Aptitude"
            ]
            selected_domain = st.selectbox("Select Domain to Drill:", options=DOMAINS, index=0)
            topic_query = None if selected_domain == "All Domains" else selected_domain
        with col_flt2:
            st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
            refresh_qs = st.button("🔄 Load New Practice Questions", use_container_width=True)

        if "drill_questions" not in st.session_state or refresh_qs or st.session_state.get("last_domain") != selected_domain:
            st.session_state["drill_questions"] = practice_svc.get_practice_questions(topic=topic_query, limit=4)
            st.session_state["last_domain"] = selected_domain
            # Clear radio selection states from previous questions
            for k in list(st.session_state.keys()):
                if k.startswith("mcq_") or k.startswith("sub_mcq_"):
                    del st.session_state[k]
            if refresh_qs:
                st.toast("Loaded fresh set of practice questions!", icon="🔄")

        drill_qs = st.session_state.get("drill_questions", [])

        if not drill_qs:
            st.info("No practice questions found for this topic filter. Try selecting 'All Domains'.")
        else:
            for idx, q in enumerate(drill_qs):
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid #6366f1; padding-left: 0.8rem; margin: 1.2rem 0 0.4rem 0;">
                            <span style="font-size: 0.78rem; color: #818cf8; font-weight: 600;">
                                DRILL #{idx + 1} &nbsp;|&nbsp; {q.topic} ({q.difficulty})
                            </span>
                            <div style="font-weight: 600; font-size: 1rem; color: #f8fafc; margin-top: 0.2rem;">
                                {q.question_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if q.code_snippet:
                        st.code(q.code_snippet)

                    choice_labels = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q.options)]
                    user_choice = st.radio(
                        f"Choose your answer for Drill #{idx + 1}:",
                        options=range(len(q.options)),
                        format_func=lambda i: choice_labels[i],
                        key=f"mcq_{q.id}",
                        index=None
                    )

                    if st.button(f"Submit Answer #{idx + 1}", key=f"sub_mcq_{q.id}"):
                        if user_choice is None:
                            st.warning("Please select an option before submitting.")
                        else:
                            sub_req = PracticeSubmissionRequest(
                                student_id=student_id,
                                question_id=q.id,
                                selected_option_index=user_choice,
                                time_spent_seconds=45
                            )
                            result = practice_svc.submit_practice_attempt(sub_req)
                            if result.is_correct:
                                st.success(f"✅ Correct! +{result.points_awarded} Points. {result.feedback}")
                            else:
                                st.error(f"❌ Incorrect. The correct answer was: Option {chr(65 + (result.correct_option_index or 0))}. {result.feedback}")
                            st.info(f"💡 **Explanation:** {result.explanation}")

    # --------------------------------------------------------------------------
    # TAB 2: Algorithmic Coding Challenges
    # --------------------------------------------------------------------------
    with tab_coding:
        st.markdown("#### 💻 Conceptual Algorithmic & SQL Coding Runner")
        
        snippets = practice_svc.get_coding_snippets()
        snippet_titles = [f"{s.title} ({s.topic} - {s.difficulty})" for s in snippets]
        selected_idx = st.selectbox("Select Challenge:", range(len(snippets)), format_func=lambda i: snippet_titles[i])
        
        active_snippet = snippets[selected_idx]

        st.markdown(
            f"""
            <div class="kpi-card" style="padding: 1.2rem; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #f8fafc;">{active_snippet.title}</h3>
                    <span style="font-size: 0.78rem; background: rgba(99,102,241,0.2); color: #a5b4fc; padding: 0.2rem 0.6rem; border-radius: 4px;">
                        {active_snippet.difficulty}
                    </span>
                </div>
                <p style="font-size: 0.95rem; color: #cbd5e1; margin: 0.7rem 0;">
                    {active_snippet.problem_statement}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("💡 Need a hint?"):
            st.write(active_snippet.hint)

        code_input = st.text_area(
            "Code Editor:",
            value=active_snippet.code_starter,
            height=200,
            key=f"code_{active_snippet.id}"
        )

        col_run, col_sol = st.columns(2)
        with col_run:
            if st.button("▶️ Run & Submit Code", type="primary", use_container_width=True):
                sub_req = PracticeSubmissionRequest(
                    student_id=student_id,
                    snippet_id=active_snippet.id,
                    code_submission=code_input,
                    time_spent_seconds=180
                )
                res = practice_svc.submit_practice_attempt(sub_req)
                if res.is_correct:
                    st.success(f"🎉 Solved! +{res.points_awarded} Points awarded. Daily streak extended to {res.current_streak} days!")
                else:
                    st.warning("⚠️ Code submitted. Implement complete algorithmic logic to earn maximum points.")
                st.markdown(res.explanation)

        with col_sol:
            if st.button("👁️ Reveal Optimal Solution", use_container_width=True):
                st.markdown("##### 🌟 Optimal Reference Implementation")
                st.code(active_snippet.optimal_solution, language="python")
                st.caption(f"Complexity: Time {active_snippet.time_complexity} | Space {active_snippet.space_complexity}")

finally:
    db.close()
