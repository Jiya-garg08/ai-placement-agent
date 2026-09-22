import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from database.database import SessionLocal
from database.models.student import User, StudentProfile
from mcp_service.tools.github_tool import get_github_portfolio

st.set_page_config(
    page_title="Student Profile & Portfolio | AI Placement Agent",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

student_id = st.session_state.get("student_id", 1)
profile = get_student_profile_data(student_id)

if not profile:
    st.error("No candidate profile found. Please create or seed a candidate in the sidebar.")
    st.stop()

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem;">👤 Student Profile & Portfolio</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Manage target career goals, academic details, and technical GitHub portfolio.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Target: {profile['target_role']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tab_profile, tab_github, tab_new_student = st.tabs([
    "📋 Academic & Career Profile",
    "🐙 GitHub Portfolio (MCP)",
    "➕ Onboard New Candidate"
])

# ------------------------------------------------------------------------------
# TAB 1: Academic & Career Profile
# ------------------------------------------------------------------------------
with tab_profile:
    st.markdown("#### 🎯 Placement Goal & Academic Background")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input("Full Name", value=profile["name"])
            email_input = st.text_input("Email Address", value=profile["email"])
            
            ROLE_OPTIONS = [
                # Engineering & Tech
                "Software Development Engineer (SDE 1)",
                "Full Stack Developer",
                "Backend Systems Engineer",
                "Cloud & DevOps Engineer",
                "Data Scientist / Machine Learning Engineer",
                # Business, Product & Management
                "Product Manager (APM / PM)",
                "Data & Business Analyst",
                "Growth & Digital Marketing Specialist",
                "Financial Analyst",
                "UI/UX & Product Designer",
                "Human Resources / Talent Specialist",
                "Operations & Supply Chain Manager",
                "Management Consultant"
            ]
            current_role = profile["target_role"]
            role_idx = ROLE_OPTIONS.index(current_role) if current_role in ROLE_OPTIONS else 0
            target_role = st.selectbox("Target Role", options=ROLE_OPTIONS, index=role_idx)

            TIER_OPTIONS = ["Tier 1 / Product", "Tier 2 / High-Growth", "Tier 3 / Enterprise Services"]
            curr_tier = profile["target_company_tier"]
            tier_idx = TIER_OPTIONS.index(curr_tier) if curr_tier in TIER_OPTIONS else 0
            company_tier = st.selectbox("Target Company Tier", options=TIER_OPTIONS, index=tier_idx)

        with col2:
            college = st.text_input("College / University", value=profile["college"])
            
            grad_cols = st.columns(2)
            with grad_cols[0]:
                grad_year = st.number_input("Graduation Year", min_value=2024, max_value=2030, value=profile["graduation_year"])
            with grad_cols[1]:
                semester = st.number_input("Current Semester", min_value=1, max_value=10, value=profile["current_semester"])

            career_goal = st.text_area(
                "Primary Career Goal",
                value=profile["career_goal"],
                help="Describe your dream placement offer and desired technical focus."
            )

        st.markdown("##### 🛠️ Primary Core Skills & Competencies")
        ALL_SKILLS = [
            # Technical & CS
            "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL",
            "Data Structures", "Algorithms", "System Design", "Operating Systems",
            "Computer Networks", "Database Management Systems", "FastAPI", "React",
            "Docker", "Kubernetes", "Git", "Machine Learning",
            # Product, Data & Strategy
            "Product Management", "Roadmapping", "A/B Testing", "User Research", "Agile",
            "Business Intelligence", "PowerBI", "Tableau", "Excel",
            # Finance, Marketing, HR & Design
            "Financial Modeling", "Budgeting", "Valuation",
            "Digital Marketing", "SEO", "Content Strategy", "Social Media Marketing",
            "UI/UX Design", "Figma", "Talent Acquisition"
        ]
        curr_skills = [s for s in profile["primary_skills"] if s in ALL_SKILLS]
        selected_skills = st.multiselect(
            "Select all core skills in your current skill stack:",
            options=ALL_SKILLS,
            default=curr_skills
        )

        submitted = st.form_submit_button("💾 Save Profile Changes", use_container_width=True)
        if submitted:
            db = SessionLocal()
            try:
                prof_rec = db.query(StudentProfile).filter_by(id=profile["id"]).first()
                user_rec = db.query(User).filter_by(id=profile["user_id"]).first()
                if prof_rec and user_rec:
                    user_rec.name = name_input.strip()
                    
                    new_email = email_input.strip().lower()
                    if new_email and new_email != user_rec.email.lower():
                        conflict = db.query(User).filter(User.email == new_email, User.id != user_rec.id).first()
                        if conflict:
                            st.error(f"Email '{new_email}' is already in use by another candidate.")
                            db.close()
                            st.stop()
                        user_rec.email = new_email

                    prof_rec.target_role = target_role
                    prof_rec.target_company_tier = company_tier
                    prof_rec.college = college.strip()
                    prof_rec.graduation_year = int(grad_year)
                    prof_rec.current_semester = int(semester)
                    prof_rec.career_goal = career_goal.strip()
                    prof_rec.primary_skills = selected_skills
                    db.commit()

                    st.toast("Profile updated successfully!", icon="✅")
                    st.rerun()
            finally:
                db.close()

# ------------------------------------------------------------------------------
# TAB 2: GitHub Portfolio Intelligence (MCP Tool)
# ------------------------------------------------------------------------------
with tab_github:
    st.markdown("#### 🐙 Live GitHub Portfolio Inspection via MCP")
    st.markdown(
        "Analyze candidate's public open-source activity, repository complexity, and technical consistency."
    )

    col_gh_in, col_gh_btn = st.columns([0.7, 0.3])
    with col_gh_in:
        gh_user = st.text_input("GitHub Username", value="Jiya-garg08", placeholder="e.g. Jiya-garg08")
    with col_gh_btn:
        st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
        sync_portfolio = st.button("🔍 Sync GitHub Portfolio", use_container_width=True)

    if sync_portfolio or "portfolio_data" in st.session_state:
        if sync_portfolio:
            with st.spinner("Querying GitHub MCP tool..."):
                st.session_state["portfolio_data"] = get_github_portfolio(gh_user)

        data = st.session_state["portfolio_data"]
        if data.get("status") == "success":
            st.success(f"Portfolio retrieved for **@{data['username']}**")

            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Public Repositories", data.get("public_repo_count", 0))
            with kpi2:
                st.metric("Total Stargazers", f"⭐ {data.get('total_stars', 0)}")
            with kpi3:
                langs = ", ".join(data.get("top_languages", []))
                st.metric("Primary Tech Stack", langs[:25])

            st.markdown("##### 🌟 Featured Projects")
            projects = data.get("featured_projects", [])
            if projects:
                for proj in projects:
                    st.markdown(
                        f"""
                        <div class="kpi-card" style="margin-bottom: 0.8rem; padding: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; font-size: 1.05rem; color: #818cf8;">
                                    📦 {proj['name']}
                                </span>
                                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.08); padding: 0.2rem 0.5rem; border-radius: 4px; color: #cbd5e1;">
                                    {proj['language']} &nbsp;|&nbsp; ⭐ {proj['stars']}
                                </span>
                            </div>
                            <p style="font-size: 0.86rem; color: #94a3b8; margin: 0.4rem 0 0.6rem 0;">
                                {proj['description']}
                            </p>
                            <a href="{proj.get('html_url', '#')}" target="_blank" style="font-size: 0.8rem; color: #38bdf8; text-decoration: none;">
                                View Repository on GitHub ↗
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No public non-forked repositories found.")
        else:
            st.error(data.get("message", "Could not fetch GitHub portfolio."))

# ------------------------------------------------------------------------------
# TAB 3: Onboard New Student
# ------------------------------------------------------------------------------
with tab_new_student:
    st.markdown("#### ➕ Register a New Candidate")
    st.markdown("Create an independent profile to test multi-candidate placement readiness.")

    with st.form("new_candidate_form"):
        new_name = st.text_input("Candidate Name", placeholder="e.g. Alex Rivera")
        new_email = st.text_input("Candidate Email", placeholder="e.g. alex.rivera@example.com")
        new_role = st.selectbox(
            "Target Role",
            options=[
                "Software Development Engineer (SDE 1)",
                "Full Stack Developer",
                "Backend Systems Engineer",
                "Cloud & DevOps Engineer",
                "Data Scientist / Machine Learning Engineer",
                "Product Manager (APM / PM)",
                "Data & Business Analyst",
                "Growth & Digital Marketing Specialist",
                "Financial Analyst",
                "UI/UX & Product Designer",
                "Human Resources / Talent Specialist",
                "Operations & Supply Chain Manager",
                "Management Consultant"
            ]
        )
        new_college = st.text_input("College", placeholder="e.g. Indian Institute of Technology")
        
        onboard_btn = st.form_submit_button("✨ Onboard Candidate", use_container_width=True)
        if onboard_btn:
            if not new_name.strip() or not new_email.strip():
                st.error("Please provide both name and email.")
            else:
                db = SessionLocal()
                try:
                    exists = db.query(User).filter_by(email=new_email.strip().lower()).first()
                    if exists:
                        st.warning("A candidate with this email already exists.")
                    else:
                        new_usr = User(name=new_name.strip(), email=new_email.strip().lower())
                        db.add(new_usr)
                        db.flush()

                        new_prof = StudentProfile(
                            user_id=new_usr.id,
                            target_role=new_role,
                            college=new_college.strip(),
                            graduation_year=2026,
                            current_semester=7,
                            primary_skills=["Python", "SQL", "Git"]
                        )
                        db.add(new_prof)
                        db.commit()

                        st.session_state["student_id"] = new_prof.id
                        st.toast(f"Candidate {new_name} onboarded successfully!", icon="🎉")
                        st.rerun()
                finally:
                    db.close()
