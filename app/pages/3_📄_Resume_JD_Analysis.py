import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import io
import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from services.resume_service import ResumeService
from services.jd_parser import JobDescriptionParser
from agents.resume_agent.resume_agent import ResumeAnalysisAgent
from database.database import SessionLocal
from database.models.resume import Resume, JobDescription

st.set_page_config(
    page_title="Resume & JD Analysis | AI Placement Agent",
    page_icon="📄",
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
            <h1 style="margin: 0; font-size: 2rem;">📄 Resume & JD ATS Analysis</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Dual-stream parser with automatic PII sanitization and ATS competency alignment.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Candidate: {profile['name'] if profile else 'Candidate'}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

SAMPLE_RESUME_TEXT = """Jiya Garg
Email: jiya.garg@example.com | Phone: +91-9876543210 | Bangalore, India
LinkedIn: linkedin.com/in/jiya-garg | GitHub: github.com/Jiya-garg08

PROFESSIONAL SUMMARY
Final-year Computer Science undergraduate with strong foundation in Data Structures, Algorithms, Distributed Systems, and Full-Stack Engineering. Proven ability to build scalable backend microservices in Python and Java.

TECHNICAL SKILLS
- Languages: Python, Java, C++, SQL, JavaScript
- Frameworks & Tools: FastAPI, Flask, React, Docker, Git, Linux
- Core CS: Data Structures & Algorithms, Object-Oriented Programming, Operating Systems, Database Management Systems

EDUCATION
National Institute of Technology - Bachelor of Technology in Computer Science (2022 - 2026) | CGPA: 8.8/10.0

KEY PROJECTS
- AI Placement Preparation Agent: Multi-agent system using Azure AI Search, RAG, and MCP tools for career guidance.
- Distributed KV Cache: High-throughput memory cache in Python using consistent hashing and LRU eviction.

WORK EXPERIENCE
Software Engineering Intern at Tech Corp (May 2025 - July 2025)
- Engineered asynchronous microservices processing 50k+ daily transactions with 99.9% uptime.
- Optimized slow SQL queries with B-Tree indexes, reducing p95 latency from 450ms to 65ms.
"""

JD_PRESETS = {
    "Tier 1 SDE 1 (Software Engineering)": """Software Development Engineer (SDE 1) - Tier 1 Product MNC
Experience: Entry-Level / Fresher (0-1 yrs)
Location: Bangalore / Hyderabad / Hybrid

ABOUT THE ROLE:
We are seeking a high-caliber Software Development Engineer to design and build mission-critical distributed services.

REQUIRED QUALIFICATIONS:
- Proficiency in Python, Java, or C++.
- Solid grounding in Data Structures and Algorithms with proven problem-solving abilities.
- Experience with Relational Databases, SQL queries, and ACID transactions.
- Sound understanding of Operating Systems, Memory Management, and Concurrency.

PREFERRED / NICE TO HAVE:
- Hands-on experience with Docker, Microservices, and Redis distributed caching.
- Familiarity with Cloud architectures (Azure or AWS).
""",
    "Associate Product Manager (APM / PM)": """Associate Product Manager (APM) - Tech & Business
Experience: Entry-Level / Fresher (0-1 yrs)
Location: Remote / Mumbai

ABOUT THE ROLE:
We are seeking an analytical, customer-centric Product Manager to lead product discovery, feature roadmapping, and execution.

REQUIRED QUALIFICATIONS:
- Strong understanding of Product Management, Roadmapping, and Agile / Scrum principles.
- Experience writing clear PRDs and defining Feature Prioritization.
- Solid experience in User Research, Customer Discovery, and A/B Testing.
- Excellent Stakeholder Management and cross-functional leadership.

PREFERRED / NICE TO HAVE:
- Familiarity with KPI Tracking, Product Strategy, and Go-To-Market launches.
- Working knowledge of SQL or Business Intelligence for data exploration.
""",
    "Data & Business Analyst (Analytics)": """Data & Business Analyst - Business Intelligence
Experience: Junior (1-3 yrs)
Location: Gurgaon / Hybrid

ABOUT THE ROLE:
Join our analytics team to transform complex datasets into actionable executive insights and dashboards.

REQUIRED QUALIFICATIONS:
- Advanced proficiency in SQL, Excel, and Spreadsheets.
- Hands-on experience with Business Intelligence tools: PowerBI or Tableau.
- Strong understanding of Statistics, Data Visualization, and KPI Tracking.
- Experience building interactive dashboards and exploratory data reports.

PREFERRED / NICE TO HAVE:
- Experience with Python, Pandas, or ETL pipelines.
- Familiarity with Google Analytics and Looker.
""",
    "Growth & Digital Marketing Specialist (Marketing)": """Growth & Digital Marketing Specialist
Experience: Entry-Level / Fresher (0-1 yrs)
Location: Bangalore / Remote

ABOUT THE ROLE:
Drive acquisition, engagement, and conversion across multiple inbound and performance marketing channels.

REQUIRED QUALIFICATIONS:
- Deep expertise in Digital Marketing, SEO, and Content Strategy.
- Experience in Social Media Marketing, Copywriting, and Campaign Management.
- Familiarity with Conversion Optimization, SEM, and Email Marketing.
- Analytical mindset with hands-on knowledge of Google Analytics.

PREFERRED / NICE TO HAVE:
- Familiarity with CRM systems (Hubspot or Salesforce).
- Experience in B2B SaaS marketing or Brand Management.
""",
    "Financial Analyst (Finance & Strategy)": """Financial Analyst - Corporate Finance & Strategy
Experience: Junior (1-3 yrs)
Location: Mumbai / Bangalore

ABOUT THE ROLE:
Provide financial modeling, budgeting, and performance forecasting to support executive corporate strategy.

REQUIRED QUALIFICATIONS:
- Strong skills in Financial Modeling, Accounting, and Valuation.
- Experience in Budgeting, Forecasting, and Financial Analysis.
- High proficiency in Excel, Spreadsheets, and Corporate Finance principles.
- Experience with P&L Management and Cash Flow analysis.

PREFERRED / NICE TO HAVE:
- Familiarity with Risk Management and Auditing standards.
- Experience with PowerBI or Business Intelligence tools.
"""
}

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 1. Candidate Resume")
    use_sample_resume = st.checkbox("Use Built-in Sample Resume", value=False)
    
    uploaded_file = st.file_uploader(
        "Upload Resume from ANY field (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        disabled=use_sample_resume
    )

    if not use_sample_resume and not uploaded_file:
        st.info("Upload your resume file above, or check 'Use Built-in Sample Resume'. Supports all industries: Tech, Product, Marketing, Finance, HR, Design, Operations.")

with col_right:
    st.markdown("#### 2. Target Job Description (JD)")
    jd_preset_options = list(JD_PRESETS.keys()) + ["Custom Job Description"]
    jd_preset = st.selectbox(
        "Select Target JD Preset",
        options=jd_preset_options
    )
    if jd_preset in JD_PRESETS:
        jd_input_text = st.text_area("Job Description Text", value=JD_PRESETS[jd_preset], height=240)
    else:
        jd_input_text = st.text_area("Paste Target Job Description (Any Domain)", height=240, placeholder="Paste JD requirements from any field or industry here...")

if "analysis_result" in st.session_state and st.session_state["analysis_result"].get("student_id") != student_id:
    del st.session_state["analysis_result"]

analyze_btn = st.button("🚀 Analyze Resume & JD Alignment", use_container_width=True, type="primary")

if analyze_btn or "analysis_result" in st.session_state:
    if analyze_btn:
        with st.spinner("Executing dual-stream parsing and PII redaction..."):
            # 1. Parse Resume (prioritize user upload)
            if uploaded_file and not use_sample_resume:
                file_name = uploaded_file.name
                parsed_resume = ResumeService.parse_resume(uploaded_file, file_name)
            else:
                file_name = "sample_resume.txt"
                stream = io.BytesIO(SAMPLE_RESUME_TEXT.encode("utf-8"))
                parsed_resume = ResumeService.parse_resume(stream, file_name)

            # 2. Parse JD
            parsed_jd = JobDescriptionParser.parse(jd_input_text)

            # 3. Analyze Resume via Agent
            agent = ResumeAnalysisAgent()
            extracted_resume = agent.analyze(parsed_resume)

            # 4. Compute Match
            resume_skills_lower = {s.lower() for s in extracted_resume.skills}
            required_skills = parsed_jd.required_skills
            preferred_skills = parsed_jd.preferred_skills

            matched_required = [s for s in required_skills if s.lower() in resume_skills_lower]
            missing_required = [s for s in required_skills if s.lower() not in resume_skills_lower]
            matched_preferred = [s for s in preferred_skills if s.lower() in resume_skills_lower]
            missing_preferred = [s for s in preferred_skills if s.lower() not in resume_skills_lower]

            total_req = max(len(required_skills), 1)
            req_score = (len(matched_required) / total_req) * 80.0
            pref_score = (len(matched_preferred) / max(len(preferred_skills), 1)) * 20.0 if preferred_skills else 20.0
            total_match_score = round(min(req_score + pref_score, 100.0), 1)

            # 5. Persist to SQLite Database for Active Student
            db_save = SessionLocal()
            try:
                from database.models.student import User
                existing_res = db_save.query(Resume).filter_by(profile_id=student_id).first()
                if not existing_res:
                    existing_res = Resume(profile_id=student_id, file_name=file_name, raw_text="", redacted_text="")
                    db_save.add(existing_res)

                existing_res.file_name = file_name
                existing_res.raw_text = parsed_resume.raw_text
                existing_res.redacted_text = parsed_resume.redacted_text
                existing_res.extracted_skills = extracted_resume.skills
                existing_res.extracted_education = [e.model_dump() for e in extracted_resume.education]
                existing_res.extracted_experience = [e.model_dump() for e in extracted_resume.experience]
                existing_res.extracted_projects = [p.model_dump() for p in extracted_resume.projects]
                existing_res.summary = extracted_resume.summary

                existing_jd = db_save.query(JobDescription).filter_by(profile_id=student_id).first()
                if not existing_jd:
                    existing_jd = JobDescription(profile_id=student_id, raw_text="")
                    db_save.add(existing_jd)

                existing_jd.role_title = parsed_jd.role_title
                existing_jd.experience_level = parsed_jd.experience_level
                existing_jd.required_skills = parsed_jd.required_skills
                existing_jd.preferred_skills = parsed_jd.preferred_skills
                existing_jd.domain_keywords = parsed_jd.domain_keywords
                existing_jd.raw_text = jd_input_text

                prof_rec = db_save.query(StudentProfile).filter_by(id=student_id).first()
                if prof_rec:
                    if extracted_resume.candidate_name and extracted_resume.candidate_name not in ("Candidate", ""):
                        user_rec = db_save.query(User).filter_by(id=prof_rec.user_id).first()
                        if user_rec:
                            user_rec.name = extracted_resume.candidate_name
                    if extracted_resume.skills:
                        prof_rec.primary_skills = extracted_resume.skills
                    if parsed_jd.role_title and parsed_jd.role_title != "Professional Role":
                        prof_rec.target_role = parsed_jd.role_title

                from database.models.skill_gap import SkillGap
                from services.next_action_service import NextActionService

                existing_gap = db_save.query(SkillGap).filter_by(profile_id=student_id).first()
                if not existing_gap:
                    existing_gap = SkillGap(profile_id=student_id)
                    db_save.add(existing_gap)
                existing_gap.strong_skills = matched_required + matched_preferred
                existing_gap.weak_skills = []
                existing_gap.missing_skills = missing_required + missing_preferred
                existing_gap.overall_readiness_score = total_match_score

                db_save.commit()

                # Refresh personalized next best actions for candidate
                try:
                    next_svc = NextActionService(session=db_save)
                    next_svc.generate_next_actions(student_id)
                except Exception:
                    pass
            finally:
                db_save.close()

            st.session_state["analysis_result"] = {
                "student_id": student_id,
                "parsed_resume": parsed_resume,
                "extracted_resume": extracted_resume,
                "parsed_jd": parsed_jd,
                "total_match_score": total_match_score,
                "matched_required": matched_required,
                "missing_required": missing_required,
                "matched_preferred": matched_preferred,
                "missing_preferred": missing_preferred
            }

    res = st.session_state["analysis_result"]
    score = res["total_match_score"]
    score_color = "#10b981" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Alignment Telemetry")

    score_col1, score_col2, score_col3, score_col4 = st.columns(4)
    with score_col1:
        st.metric(
            label="Overall ATS Match Score",
            value=f"{score:.1f}%",
            delta="Strong Match" if score >= 75 else "Competency Gaps Detected"
        )
    with score_col2:
        st.metric(
            label="Required Skills Met",
            value=f"{len(res['matched_required'])} / {len(res['parsed_jd'].required_skills)}"
        )
    with score_col3:
        st.metric(
            label="Bonus / Preferred Skills Met",
            value=f"{len(res['matched_preferred'])} / {len(res['parsed_jd'].preferred_skills)}"
        )
    with score_col4:
        st.metric(
            label="Experience Level Match",
            value=res["parsed_jd"].experience_level[:16]
        )

    t1, t2, t3, t4 = st.tabs([
        "🎯 Competency Match Breakdown",
        "🔒 PII-Sanitized Resume Preview",
        "📋 JD Taxonomy & Keywords",
        "💡 AI Optimization Advice"
    ])

    with t1:
        st.markdown("#### Competency Alignment Grid")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### 🟢 Matched Mandatory Skills")
            if res["matched_required"]:
                for s in res["matched_required"]:
                    st.markdown(f"- ✅ **{s}** *(Verified in Resume)*")
            else:
                st.write("No mandatory skills matched yet.")

            st.markdown("##### 🟡 Matched Preferred Skills")
            if res["matched_preferred"]:
                for s in res["matched_preferred"]:
                    st.markdown(f"- 🌟 **{s}** *(Bonus Skill)*")
            else:
                st.write("No preferred skills matched.")

        with col_m2:
            st.markdown("##### 🔴 Missing Mandatory Skills")
            if res["missing_required"]:
                for s in res["missing_required"]:
                    st.markdown(f"- ❌ **{s}** *(Required for role)*")
            else:
                st.success("All mandatory skills satisfied!")

            st.markdown("##### ⚪ Missing Preferred Skills")
            if res["missing_preferred"]:
                for s in res["missing_preferred"]:
                    st.markdown(f"- ⏳ **{s}** *(Recommended)*")

    with t2:
        st.markdown("#### 🔒 Privacy-Compliant PII Redaction")
        st.info("Personal Identifiable Information (Emails, phone numbers, addresses) has been automatically scrubbed in accordance with recruiting privacy guidelines.")
        st.text_area("Anonymized Resume Stream", value=res["parsed_resume"].redacted_text, height=320, disabled=True)

    with t3:
        st.markdown("#### 📋 Target Job Description Profile")
        st.write(f"**Target Role:** {res['parsed_jd'].role_title}")
        st.write(f"**Experience Requirement:** {res['parsed_jd'].experience_level}")
        st.write(f"**Domain Keywords:** {', '.join(res['parsed_jd'].domain_keywords)}")

    with t4:
        st.markdown("#### 💡 Technical Recruiter Feedback")
        missing = res["missing_required"] + res["missing_preferred"]
        if missing:
            st.markdown(f"To raise your ATS match score above **90%**, incorporate demonstrated project experience with:")
            for m in missing[:4]:
                st.markdown(f"1. **{m}**: Add practical implementations, measurable metrics, or coursework covering {m}.")
        else:
            st.success("Excellent alignment! Your resume satisfies both core and preferred requirements for this role.")
