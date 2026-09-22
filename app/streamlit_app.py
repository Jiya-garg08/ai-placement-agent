import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data

# Configure page layout and metadata
st.set_page_config(
    page_title="AI Placement Preparation Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render universal sidebar with student switcher
render_sidebar()

# Active profile data
student_id = st.session_state.get("student_id", 1)
profile = get_student_profile_data(student_id)

# Main Page Content
st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%);
                border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 14px; padding: 1.8rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 style="margin: 0; font-size: 2.1rem; color: #f8fafc;">
                    🎓 AI Placement Preparation Agent
                </h1>
                <p style="margin: 0.4rem 0 0 0; font-size: 1.05rem; color: #94a3b8;">
                    Autonomous, multi-agent AI accelerator guiding candidates from profile diagnosis to job offer.
                </p>
            </div>
            <div style="display: flex; gap: 0.8rem;">
                <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4);
                             color: #34d399; font-size: 0.82rem; font-weight: 600; padding: 0.35rem 0.8rem; border-radius: 9999px;">
                    🟢 Swarm Active (Mock Mode)
                </span>
                <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4);
                             color: #93c5fd; font-size: 0.82rem; font-weight: 600; padding: 0.35rem 0.8rem; border-radius: 9999px;">
                    💰 $0.00 / $200.00 Spent
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if profile:
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(
            label="Active Candidate",
            value=profile["name"],
            delta=profile["college"][:18]
        )
    with col_kpi2:
        st.metric(
            label="Target Career Goal",
            value=profile["target_role"].split("(")[0].strip()[:20],
            delta=profile["target_company_tier"]
        )
    with col_kpi3:
        st.metric(
            label="Placement Readiness",
            value=f"{profile['readiness_score']:.1f}%",
            delta="Ready for Interviews" if profile["readiness_score"] >= 75 else "Developing"
        )
    with col_kpi4:
        st.metric(
            label="Preparation Streak",
            value=f"{profile['current_streak']} Days 🔥",
            delta=f"{profile['total_questions_solved']} Solved"
        )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# System Architecture & Capabilities Callout
st.markdown("### 🗺️ Preparation Journey & Platform Modules")
st.markdown(
    "Select any module from the sidebar or click a quick-jump card below to continue your placement preparation:"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">📊 <b>1. Dashboard</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Unified command center with real-time placement readiness gauge, domain radar chart, and top Next Best Actions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Dashboard →", key="btn_dash", use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">👤 <b>2. Profile & Portfolio</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Manage target role, academic semester, target tier, and query live GitHub repository tools via MCP.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">📄 <b>3. Resume & JD Analysis</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Dual parser scrubbing sensitive PII, extracting competencies, and calculating ATS role alignment scores.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">📝 <b>4. Diagnostic Exam</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Timed 10-question multi-domain assessment establishing empirical benchmark accuracy across CS domains.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">🔍 <b>5. Skill Gap Matrix</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Triangulates resume strengths, test accuracy, and target JD requirements into prioritized competency gaps.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">📅 <b>6. Learning Plan</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Structured 4-week chronological roadmap with weekly objectives, daily hours, and milestone trackers.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">🤖 <b>7. Grounded RAG Tutor</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Pedagogical AI tutor backed by hybrid vector search and strict source citations to prevent hallucinations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">💻 <b>8. Interactive Practice</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Conceptual coding snippet runner, algorithmic drills, hint reveals, and daily streak gamification.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi-card" style="min-height: 200px;">
            <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">🎯 <b>9-10. Next Best Action</b></div>
            <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem;">
                Prioritized tactical actions dynamically calibrated against your latest diagnostic weak spots.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Agent Swarm Architecture Footer
with st.expander("ℹ️ Multi-Agent Swarm Architecture & Safety Framework"):
    st.markdown(
        """
        - **Microsoft Foundry Master Orchestrator**: Intent classifier routing candidate inquiries across 6 subagents.
        - **Model Context Protocol (MCP)**: Sandboxed tool interface reading profile attributes, progress summaries, and GitHub repos.
        - **Safety Boundaries**: Rate limiter (60 rpm token cap), response cache (TTL 300s), and thread-pool execution timeouts (15s).
        - **Azure Spend Guard**: Operating strictly in zero-cost mock mode (`AZURE_MOCK_MODE=True`) maintaining $0.00 spend on the $200 Azure grant.
        """
    )
