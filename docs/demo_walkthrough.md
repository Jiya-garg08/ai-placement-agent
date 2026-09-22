# 🎬 Product Demonstration Script (5-Minute Walkthrough)

**Project**: AI Placement Preparation Agent  
**Candidate Demo Profile**: Jiya Garg (Target Role: Full Stack Engineer / SDE-1)  
**Total Target Duration**: ~5 Minutes  

---

## ⏱️ Timeline & Agenda Overview

| Time | Stage / Page | Core Focus |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **Executive Intro & Dashboard** | Platform overview, radar chart vs Tier-1 benchmark, Next Best Action cards. |
| **0:45 - 1:15** | **Profile & MCP Tool Sync** | Student profile editor, Model Context Protocol GitHub portfolio inspection. |
| **1:15 - 1:55** | **Resume & JD Analysis** | Dual-stream parsing, PII redaction, ATS match score (85%), and keyword alignment. |
| **1:55 - 2:35** | **Diagnostic Assessment** | 10-question MCQ quiz runner, instant scoring, topic breakdown. |
| **2:35 - 3:10** | **Skill Gap Matrix** | 3-way triangulation (Strong, Weak, Missing skills) across technical domains. |
| **3:10 - 3:45** | **Adaptive Learning Roadmap** | 4-week chronological plan, interactive status toggling (Pending/Done). |
| **3:45 - 4:25** | **Grounded RAG Tutor & Practice** | Hybrid Azure search retrieval, textbook citations, MCQ drills & code runner. |
| **4:25 - 5:00** | **Performance & Next Best Action** | Hiring manager qualitative appraisal, empirical priority execution, cost guardrails ($0 spent). |

---

## 🎙️ Scene-by-Scene Script

### Scene 1: Executive Overview & Dashboard (0:00 - 0:45)
- **URL / Screen**: `http://localhost:8501` -> `1_📊_Dashboard`
- **Visual**:
  - Show the glassmorphic dark theme, candidate selector (`Jiya Garg - Full Stack Engineer`), readiness score (`78%`), and streak count (`5 days`).
  - Point to the **Azure Spend Monitor** in the sidebar: `$0.00 / $200.00 (Mock Mode Active)`.
  - Highlight the interactive Plotly radar chart comparing Jiya's current mastery against the Tier-1 tech industry benchmark.
- **Narrator Script**:
  > *"Welcome to the AI Placement Preparation Agent — an enterprise multi-agent career acceleration platform built with Microsoft Foundry, Azure AI Search, and the Model Context Protocol.*
  >
  > *Students preparing for top tech placements often suffer from fragmented preparation: they don't know where they stand compared to industry benchmarks or what to study next. Our platform solves this end-to-end. Here on the executive dashboard, we see candidate Jiya Garg with a 78% Placement Readiness Index, a 5-day practice streak, and an interactive radar benchmark pinpointing strong domains like Python and DBMS alongside growth opportunities in System Design and Dynamic Programming.*
  >
  > *Notice our sidebar budget guardrail: through high-fidelity mock orchestration, all features execute offline at exactly zero dollars."*

---

### Scene 2: Student Profile & MCP GitHub Sync (0:45 - 1:15)
- **URL / Screen**: `app/pages/2_👤_Student_Profile.py`
- **Visual**:
  - Show candidate college, degree, target graduation, and target role.
  - Scroll down to the **Model Context Protocol (MCP) GitHub Integration** section.
  - Click **"Sync GitHub Portfolio via MCP"**.
  - Show retrieved repositories (`ai-placement-agent`, `cloud-native-microservices`), detected languages, and primary framework badges.
- **Narrator Script**:
  > *"In the Student Profile module, candidates configure their placement preferences. But rather than relying only on self-reported skills, the platform leverages the Model Context Protocol (MCP) to securely query the candidate's live GitHub profile. In one click, our MCP GitHub tool inspects public repositories, star counts, and dominant languages, directly grounding the agent swarm in the student's actual code contributions."*

---

### Scene 3: Resume & Job Description Analysis (1:15 - 1:55)
- **URL / Screen**: `app/pages/3_📄_Resume_JD_Analysis.py`
- **Visual**:
  - Select pre-loaded sample resume and target Job Description (`Senior Software Engineer / SDE-1`).
  - Click **"Analyze Resume Against Target JD"**.
  - Observe the PII Redaction notice (phone numbers and emails automatically masked for privacy).
  - Review the **85% ATS Compatibility Score**, matched competencies (`FastAPI`, `PostgreSQL`, `Docker`), and recommended keyword additions (`Kubernetes`, `Redis`).
- **Narrator Script**:
  > *"Next, the candidate uploads their resume alongside a target job description. The Resume Analysis Agent parses unstructured documents via PDF and text streams. Notice our enterprise privacy layer: candidate phone numbers and emails are automatically scrubbed via PII redaction before LLM processing.*
  >
  > *The engine deterministically calculates an ATS alignment score — here 85% — extracting matched competencies and highlighting missing keywords required for recruiter screening."*

---

### Scene 4: Calibrated Diagnostic Assessment (1:55 - 2:35)
- **URL / Screen**: `app/pages/4_📝_Diagnostic_Assessment.py`
- **Visual**:
  - View the 10-question technical diagnostic exam.
  - Answer questions across Binary Search Trees, Dynamic Programming, ACID transactions, and Deadlocks.
  - Click **"Submit Assessment"**.
  - View the instant score report (e.g. 80%), answer explanations, and breakdown of correct vs incorrect responses.
- **Narrator Script**:
  > *"To ensure recommendations aren't based on guesswork, the Assessment Agent administers a 10-question diagnostic test spanning CS core fundamentals: DSA, Operating Systems, DBMS, and System Design.*
  >
  > *Upon submission, the submission is recorded in our SQLite database, grading each question deterministically and generating clear conceptual explanations for any missed questions."*

---

### Scene 5: Skill Gap Triangulation (2:35 - 3:10)
- **URL / Screen**: `app/pages/5_🔍_Skill_Gap.py`
- **Visual**:
  - Show the triangulated matrix comparing:
    1. Resume declared skills
    2. JD target requirements
    3. Diagnostic test results
  - Show the 3 columns:
    - 🟢 **Strong Competencies** (High proficiency confirmed by test & resume)
    - 🟡 **Weak Areas** (Present on resume or JD, but low quiz score)
    - 🔴 **Missing Topics** (Required by JD, absent from resume)
- **Narrator Script**:
  > *"Here is where our deterministic intelligence shines: the Skill Gap Matrix. Rather than an arbitrary summary, it performs a 3-way triangulation between what the candidate claims on their resume, what the employer requires, and how they actually performed on the diagnostic test.*
  >
  > *This isolates high-priority weak spots — such as B-Trees and Distributed Caching — preventing wasted study time."*

---

### Scene 6: Adaptive 4-Week Learning Roadmap (3:10 - 3:45)
- **URL / Screen**: `app/pages/6_📅_Learning_Plan.py`
- **Visual**:
  - Show the week-by-week curriculum:
    - Week 1: Core Algorithms & Advanced Data Structures
    - Week 2: DBMS Internals & Query Optimization
    - Week 3: Operating Systems & Concurrency
    - Week 4: System Design & Mock Placement Drills
  - Click the status toggle button on an item to switch it from `PENDING` to `COMPLETED`.
  - Watch the progress bar instantly update.
- **Narrator Script**:
  > *"The Planner Agent converts those identified skill gaps into an adaptive 4-week preparation plan. Each week focuses on specific remediations with daily milestones and estimated study hours. Candidates can interactively toggle task statuses, maintaining clear accountability and momentum."*

---

### Scene 7: Grounded RAG Tutor & Interactive Practice (3:45 - 4:25)
- **URL / Screen**: `app/pages/7_🤖_RAG_Tutor.py` & `app/pages/8_💻_Practice.py`
- **Visual**:
  - In RAG Tutor, type a question: *"Explain the ACID properties in database management with real-world examples."*
  - Watch the grounded response render with **verified inline citations** (`[Source 1: DBMS Fundamentals, Section 3.2]`).
  - Demonstrate out-of-domain prompt injection defense (e.g. asking for unrelated recipes or prompt override).
  - Switch to `8_💻_Practice`, solve an interactive MCQ drill, execute a Python snippet, and see the daily streak tick up.
- **Narrator Script**:
  > *"When students need conceptual depth, the RAG Tutor Agent provides grounded answers powered by Azure AI Search hybrid retrieval across our university-grade curriculum.*
  >
  > *Notice that every explanation includes verified inline citations from source texts, eliminating hallucinations. The tutor also incorporates prompt fencing to reject non-academic queries or jailbreak attempts.*
  >
  > *In the Practice module, students reinforce concepts with randomized drills and algorithmic coding tests, building daily streaks that encourage consistent practice habits."*

---

### Scene 8: Performance Analytics & Next Best Action (4:25 - 5:00)
- **URL / Screen**: `app/pages/9_📈_Performance.py` & `app/pages/10_🎯_Next_Best_Action.py`
- **Visual**:
  - View topic mastery scores and the qualitative **Hiring Manager Appraisal Report**.
  - Navigate to `10_🎯_Next_Best_Action`.
  - Inspect the top prioritized card: *"Review Dynamic Programming Memoization (Priority: HIGH)"*.
  - Click the **"Execute Action"** button to jump directly into the remediation module.
  - Conclude by highlighting the automated test suite and container architecture.
- **Narrator Script**:
  > *"Finally, the Evaluation Agent synthesizes candidate trajectory into a hiring-manager-ready appraisal, grading readiness across technical, problem-solving, and architectural pillars.*
  >
  > *The system then computes the single 'Next Best Action' — an empirical priority queue removing decision fatigue so the candidate always knows their highest-yield study task.*
  >
  > *With 113 automated tests, 89% code coverage, zero secret leaks, full Docker containerization, and a 100% free offline development mode, the AI Placement Preparation Agent is ready for institutional deployment. Thank you!"*
