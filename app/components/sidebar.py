import streamlit as st
from typing import Optional
from app.utils.ui_helpers import (
    list_all_students,
    get_student_profile_data,
    initialize_session_state,
    load_custom_css
)
from app.utils.seed_demo_student import seed_demo_candidate


def render_sidebar() -> None:
    """Universal sidebar component providing candidate switcher, profile badges, and cloud telemetry."""
    # Ensure base session state & custom styling are active
    initialize_session_state()
    load_custom_css()

    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.2rem;">
                <h2 style="margin: 0; font-size: 1.4rem; color: #6366f1;">🎓 Placement Agent</h2>
                <span style="font-size: 0.78rem; color: #94a3b8;">Autonomous Placement Preparation</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Candidate Switcher
        st.markdown("##### 👤 Active Candidate")
        candidates = list_all_students()

        if candidates:
            cand_options = {c["id"]: f"{c['name']} ({c['target_role'][:22]}...)" for c in candidates}
            current_id = st.session_state.get("student_id", candidates[0]["id"])
            
            # Find current index
            id_list = list(cand_options.keys())
            current_idx = id_list.index(current_id) if current_id in id_list else 0

            selected_id = st.selectbox(
                "Select Candidate Profile",
                options=id_list,
                index=current_idx,
                format_func=lambda x: cand_options[x],
                label_visibility="collapsed"
            )

            if selected_id != st.session_state.get("student_id"):
                st.session_state["student_id"] = selected_id
                st.session_state.pop("analysis_result", None)
                st.session_state.pop("active_exam_id", None)
                st.session_state.pop("exam_answers", None)
                st.session_state.pop("last_exam_result", None)
                st.session_state.pop("exam_candidate_id", None)
                st.rerun()

        # 2. Candidate Quick Summary Card
        profile_data = get_student_profile_data(st.session_state["student_id"])
        if profile_data:
            readiness = profile_data.get("readiness_score", 0.0)
            streak = profile_data.get("current_streak", 0)
            role = profile_data.get("target_role", "SDE")
            tier = profile_data.get("target_company_tier", "Tier 1")

            readiness_color = "#10b981" if readiness >= 75 else ("#f59e0b" if readiness >= 50 else "#ef4444")

            st.markdown(
                f"""
                <div class="sidebar-profile-box">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc;">
                        {profile_data['name']}
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem;">
                        🎯 {role}
                    </div>
                    <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.15rem;">
                        🏛️ {tier}
                    </div>
                    <hr style="margin: 0.7rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.8rem; color: #cbd5e1;">Readiness</span>
                        <span style="font-weight: 700; font-size: 0.95rem; color: {readiness_color};">
                            {readiness:.1f}%
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.35rem;">
                        <span style="font-size: 0.8rem; color: #cbd5e1;">Daily Streak</span>
                        <span style="font-weight: 700; font-size: 0.95rem; color: #fbbf24;">
                            🔥 {streak} Days
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 3. System & Azure Governance Telemetry
        st.markdown("##### 🛡️ Foundry AI Swarm")
        mock_active = st.session_state.get("azure_mock_mode", True)
        status_text = "Mock Mode Active" if mock_active else "Live Azure Connected"
        
        st.markdown(
            f"""
            <div class="sidebar-status-chip">
                <span>🟢</span>
                <span>{status_text}</span>
            </div>
            <div class="sidebar-cost-chip">
                <span>💰</span>
                <span>Grant: $200.00 ($0.00 spent)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 4. Quick Actions
        col_seed, col_refresh = st.columns(2)
        with col_seed:
            if st.button("🔄 Re-Seed", help="Reset and re-seed demo profile data", use_container_width=True):
                seed_demo_candidate()
                st.toast("Demo data refreshed successfully!", icon="✅")
                st.rerun()
        with col_refresh:
            if st.button("⚡ Refresh", help="Reload current telemetry", use_container_width=True):
                st.rerun()

        st.markdown(
            """
            <div style="font-size: 0.7rem; color: #475569; text-align: center; margin-top: 1.5rem;">
                AI Placement Prep Agent v1.0<br>
                Microsoft Foundry & RAG Engine
            </div>
            """,
            unsafe_allow_html=True
        )
