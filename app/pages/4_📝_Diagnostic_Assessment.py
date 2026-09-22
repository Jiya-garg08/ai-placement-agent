import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import time
from datetime import datetime
import streamlit as st

from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from services.assessment_service import AssessmentService
from schemas.assessment_schema import AssessmentSubmission, AssessmentAnswerSubmission
from database.database import SessionLocal
from database.models.assessment import Assessment, Question
from database.models.assessment_attempt import AssessmentAttempt

st.set_page_config(
    page_title="Diagnostic Assessment | AI Placement Agent",
    page_icon="📝",
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
            <h1 style="margin: 0; font-size: 2rem;">📝 Calibrated Diagnostic Assessment</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Timed technical evaluation across core computer science competencies to establish your empirical baseline.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Candidate: {profile['name'] if profile else 'Candidate'}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize and isolate exam session states per candidate
if st.session_state.get("exam_candidate_id") != student_id:
    st.session_state["exam_candidate_id"] = student_id
    st.session_state["active_exam_id"] = None
    st.session_state["exam_answers"] = {}
    st.session_state["last_exam_result"] = None

if "active_exam_id" not in st.session_state:
    st.session_state["active_exam_id"] = None
if "exam_answers" not in st.session_state:
    st.session_state["exam_answers"] = {}
if "last_exam_result" not in st.session_state:
    st.session_state["last_exam_result"] = None

db = SessionLocal()
try:
    svc = AssessmentService(session=db)

    # --------------------------------------------------------------------------
    # MODE 1: Results View (if completed recently)
    # --------------------------------------------------------------------------
    if st.session_state["last_exam_result"] is not None:
        res = st.session_state["last_exam_result"]
        pct = res["score_percentage"]
        res_color = "#10b981" if pct >= 75 else ("#f59e0b" if pct >= 50 else "#ef4444")

        st.markdown("### 🏆 Diagnostic Exam Results")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Score", f"{pct:.1f}%", delta="Placement Ready" if pct >= 75 else "Developing")
        with c2:
            st.metric("Correct Answers", f"{res['total_correct']} / {res['total_questions']}")
        with c3:
            st.metric("Questions Attempted", f"{len(res['answers_submitted'])} / {res['total_questions']}")
        with c4:
            st.metric("Attempt Status", "Submitted & Saved ✅")

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📊 Domain Mastery Breakdown")
        
        if res.get("topic_scores"):
            for ts in res["topic_scores"]:
                top_pct = ts.get("percentage", 0.0)
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.2rem;">
                        <b>{ts['topic']}</b>
                        <span>{ts['correct']}/{ts['total']} ({top_pct:.0f}%)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.progress(min(top_pct / 100.0, 1.0))

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Question Review & Pedagogical Explanations")
        
        for idx, q_info in enumerate(res["question_details"]):
            user_ans = res["user_answers_map"].get(q_info["id"])
            is_corr = (user_ans == q_info["correct_option_index"])
            
            icon = "✅" if is_corr else "❌"
            header_color = "#10b981" if is_corr else "#ef4444"

            with st.expander(f"{icon} Question {idx + 1}: {q_info['question_text'][:80]}...", expanded=(not is_corr)):
                st.markdown(f"**Topic:** `{q_info['topic']}` | **Difficulty:** `{q_info['difficulty']}`")
                st.markdown(f"**Question:** {q_info['question_text']}")
                
                if q_info.get("code_snippet"):
                    st.code(q_info["code_snippet"], language="python")

                st.markdown("##### Options:")
                for o_idx, opt in enumerate(q_info["options"]):
                    marker = ""
                    if o_idx == q_info["correct_option_index"]:
                        marker = " *(Correct Answer)*"
                    if o_idx == user_ans:
                        marker += " **<- Your Selection**"
                    st.markdown(f"- **Option {chr(65+o_idx)}:** {opt}{marker}")

                st.info(f"💡 **Explanation:** {q_info['explanation']}")

        col_next, col_retake = st.columns(2)
        with col_next:
            if st.button("Proceed to Skill Gap Matrix →", type="primary", use_container_width=True):
                st.switch_page("pages/5_🔍_Skill_Gap.py")
        with col_retake:
            if st.button("🔄 Retake Diagnostic Assessment", use_container_width=True):
                st.session_state["last_exam_result"] = None
                st.session_state["active_exam_id"] = None
                st.session_state["exam_answers"] = {}
                st.rerun()

    # --------------------------------------------------------------------------
    # MODE 2: Active Exam Runner
    # --------------------------------------------------------------------------
    elif st.session_state["active_exam_id"] is not None:
        exam_id = st.session_state["active_exam_id"]
        assessment = svc.get_assessment(exam_id)
        
        if not assessment or not assessment.questions:
            st.error("Assessment questions could not be retrieved.")
            st.session_state["active_exam_id"] = None
            st.rerun()

        col_title, col_cancel = st.columns([0.75, 0.25])
        with col_title:
            st.markdown(f"### ⏱️ {assessment.title}")
        with col_cancel:
            if st.button("❌ Exit / Recalibrate Exam", use_container_width=True, help="Discard current unsubmitted exam and recalibrate for updated role and skills"):
                st.session_state["active_exam_id"] = None
                st.session_state["exam_answers"] = {}
                st.rerun()

        st.info("Answer each question carefully. Your questions have been calibrated to your target role and skills.")

        with st.form("exam_runner_form"):
            user_selections = {}
            for idx, q in enumerate(assessment.questions):
                st.markdown(
                    f"""
                    <div style="border-left: 3px solid #6366f1; padding-left: 0.8rem; margin: 1.5rem 0 0.5rem 0;">
                        <span style="font-size: 0.78rem; color: #818cf8; font-weight: 600;">
                            QUESTION {idx + 1} OF {len(assessment.questions)} &nbsp;|&nbsp; {q.topic} ({q.difficulty})
                        </span>
                        <div style="font-weight: 600; font-size: 1.05rem; color: #f8fafc; margin-top: 0.3rem;">
                            {q.question_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if q.code_snippet:
                    st.code(q.code_snippet)

                # Format radio options
                choice_labels = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q.options)]
                selected = st.radio(
                    f"Select answer for Question {idx + 1}:",
                    options=range(len(q.options)),
                    format_func=lambda i: choice_labels[i],
                    key=f"q_{q.id}",
                    index=None
                )
                user_selections[q.id] = selected

            submit_exam = st.form_submit_button("🏁 Submit Diagnostic Assessment", type="primary", use_container_width=True)
            if submit_exam:
                answers_sub = [
                    AssessmentAnswerSubmission(
                        question_id=qid,
                        selected_option_index=ans if ans is not None else -1
                    )
                    for qid, ans in user_selections.items()
                ]
                submission = AssessmentSubmission(
                    assessment_id=exam_id,
                    profile_id=student_id,
                    answers=answers_sub
                )
                attempt = svc.record_submission(submission)

                # Prepare question review details
                q_details = []
                for q in assessment.questions:
                    q_details.append({
                        "id": q.id,
                        "topic": q.topic,
                        "difficulty": q.difficulty,
                        "question_text": q.question_text,
                        "code_snippet": q.code_snippet,
                        "options": q.options,
                        "correct_option_index": q.correct_option_index,
                        "explanation": q.explanation
                    })

                st.session_state["last_exam_result"] = {
                    "attempt_id": attempt.id,
                    "score_percentage": attempt.score_percentage,
                    "total_correct": attempt.total_correct,
                    "total_questions": attempt.total_questions,
                    "topic_scores": attempt.topic_scores,
                    "answers_submitted": [a for a in user_selections.values() if a is not None],
                    "user_answers_map": user_selections,
                    "question_details": q_details
                }
                st.session_state["active_exam_id"] = None
                st.toast("Assessment submitted successfully!", icon="🎉")
                st.rerun()

    # --------------------------------------------------------------------------
    # MODE 3: Start Exam Landing Screen
    # --------------------------------------------------------------------------
    else:
        target_role = profile["target_role"] if profile else "Software Development Engineer (SDE)"
        candidate_skills = profile.get("primary_skills", []) if profile else []
        
        from database.models.resume import Resume
        latest_resume = db.query(Resume).filter_by(profile_id=student_id).order_by(Resume.id.desc()).first()
        resume_skills = latest_resume.extracted_skills if latest_resume else []

        resolved_topics = svc.resolve_topics_for_role_and_skills(target_role, candidate_skills, resume_skills)

        st.markdown(
            f"""
            <div class="kpi-card" style="padding: 1.5rem; margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; color: #f8fafc;">📋 Role & Skill-Calibrated Diagnostic Assessment</h3>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">
                    The Placement Diagnostic Assessment dynamically adapts to your target role: 
                    <b style="color: #38bdf8;">{target_role}</b> and your verified skills.
                </p>
                <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 8px; padding: 0.8rem 1rem; margin: 1rem 0;">
                    <span style="font-size: 0.8rem; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">
                        🎯 Calibrated Evaluation Domains:
                    </span>
                    <div style="margin-top: 0.3rem; color: #f8fafc; font-weight: 500; font-size: 0.95rem;">
                        {', '.join(resolved_topics)}
                    </div>
                </div>
                <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0;">
                    <li><b>Questions:</b> 10 Multiple-Choice Questions focused specifically on your target domain</li>
                    <li><b>Time Limit:</b> 20 Minutes (recommended pace: ~2 mins/question)</li>
                    <li><b>Impact:</b> Evaluates domain strengths and generates your personalized roadmap</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Historical attempts
        attempts = db.query(AssessmentAttempt).filter_by(profile_id=student_id).order_by(AssessmentAttempt.created_at.desc()).all()
        if attempts:
            st.markdown("#### 📜 Past Assessment Attempts")
            for att in attempts[:3]:
                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>Attempt #{att.id}</b> &nbsp;|&nbsp; 
                            Score: <b style="color: #34d399;">{att.score_percentage:.1f}%</b> ({att.total_correct}/{att.total_questions} correct)
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b;">
                            {att.created_at.strftime('%b %d, %Y - %H:%M') if att.created_at else 'Recent'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        use_ai_generation = st.checkbox(
            "✨ Generate brand-new custom questions live with Microsoft Foundry (gpt-5-mini)",
            value=False,
            help="When checked, calls gpt-5-mini to synthesize 10 novel questions specifically tailored to your role and resume requirements."
        )

        if st.button(f"🚀 Begin Diagnostic Assessment for {target_role}", type="primary", use_container_width=True):
            with st.spinner(f"Calibrating 10 questions tailored to {target_role} and your verified skills..."):
                assessment = svc.create_diagnostic_assessment(
                    target_role=target_role,
                    total_questions=10,
                    candidate_skills=candidate_skills,
                    resume_skills=resume_skills,
                    use_ai_generation=use_ai_generation
                )
                st.session_state["active_exam_id"] = assessment.id
                st.rerun()

finally:
    db.close()
