import subprocess
import time
import sys

issues = [
    {
        "title": "Project Foundation & Development Environment Setup",
        "agent": "Architecture Agent",
        "phase": "Phase 0",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Initialize repository structure, virtualenv setup, Git config, CI workflow, and environment templates.

### Scope & Deliverables
- Target directory tree: app/, agents/, rag/, mcp/, database/, services/, schemas/, tests/, config/
- .gitignore, .env.example, requirements.txt, README.md, LICENSE
- .github/workflows/ci.yml with automated Pytest and flake8 linting

### Subagent Owner
Architecture Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [x] Pinned dependencies install cleanly
- [x] Base Pytest suite passes offline
- [x] GitHub Actions CI runs clean on push
"""
    },
    {
        "title": "SQLite Database Foundation & SQLAlchemy Base Repository",
        "agent": "Database Agent",
        "phase": "Phase 1",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Establish clean SQLite connection layer with SQLAlchemy 2.0 and generic BaseRepository pattern.

### Scope & Deliverables
- database/database.py: Engine, scoped session factory, Base declarative class
- database/repositories/base_repository.py: Generic CRUD operations (get, list, create, update, delete)
- In-memory SQLite support for offline testing

### Subagent Owner
Database Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Engine connects to local placement.db or in-memory SQLite
- [ ] Unit tests verify atomic transactions and rollbacks
"""
    },
    {
        "title": "User & StudentProfile ORM Models and Schemas",
        "agent": "Database Agent",
        "phase": "Phase 1",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Implement User and StudentProfile SQLAlchemy models, Pydantic validation schemas, and student repository.

### Scope & Deliverables
- database/models/student.py: User and StudentProfile tables with target role, graduation year, college
- schemas/profile_schema.py: StudentProfileCreate, StudentProfileResponse, TargetRoleUpdate
- database/repositories/student_repository.py & services/student_service.py

### Subagent Owner
Database Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Can create, retrieve, and update student profiles
- [ ] Pydantic validation rejects invalid emails or negative graduation years
"""
    },
    {
        "title": "Local Resume Parsing Engine (PDF & DOCX)",
        "agent": "Backend Agent",
        "phase": "Phase 2",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Extract raw text, section blocks, and basic metadata from uploaded PDF/DOCX resumes locally with zero cloud dependencies.

### Scope & Deliverables
- services/resume_service.py: PyPDF / pdfplumber integration
- Regex text cleaner and section header splitter (Education, Experience, Projects, Skills)
- tests/unit/test_resume_parser.py with sample resume fixtures

### Subagent Owner
Backend Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Cleanly parses multi-column and single-column PDF resumes
- [ ] Masks PII (phone numbers, email) before downstream processing
"""
    },
    {
        "title": "Job Description Parsing & Keyword Normalization Engine",
        "agent": "Backend Agent",
        "phase": "Phase 2",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Parse and tokenize technical Job Descriptions to extract required competencies, experience levels, and domain keywords.

### Scope & Deliverables
- services/jd_parser.py: Text normalizer and skill dictionary matcher
- config/constants.py: Standard taxonomy mapping (DSA, SQL, System Design, Java, Python)
- tests/unit/test_jd_parser.py

### Subagent Owner
Backend Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Matches raw JD text against standard technical skill dictionary with >90% precision
"""
    },
    {
        "title": "AI Resume Analysis Agent (Structured Entity Extraction)",
        "agent": "Foundry Agent",
        "phase": "Phase 2",
        "cost": "Low (<$0.50)",
        "desc": """### Objective
Build Microsoft Foundry / Azure OpenAI powered agent to extract structured candidate entities from raw resume text.

### Scope & Deliverables
- agents/resume_agent/resume_agent.py: System prompt and structured extraction logic
- schemas/resume_schema.py: Pydantic models for ExtractedResume (skills, projects, education, experience)
- Local mock fallback when AZURE_MOCK_MODE=True

### Subagent Owner
Foundry Agent

### Azure Cost Impact
Low (<$0.50)

### Acceptance Criteria
- [ ] Outputs 100% schema-valid JSON adhering to ResumeSchema
- [ ] Mock mode allows offline unit test execution
"""
    },
    {
        "title": "Diagnostic Assessment Engine & Question Bank Model",
        "agent": "Backend Agent",
        "phase": "Phase 3",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Design Assessment and Question database models with automated test generation rules covering 10 core placement domains.

### Scope & Deliverables
- database/models/assessment.py: Assessment and Question tables
- services/assessment_service.py: Random question sampler calibrated by role difficulty
- scripts/seed_data.py: Curated bank of 50+ seed questions across DSA, DBMS, OS, OOP, CN

### Subagent Owner
Backend Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Generates randomized 10-question diagnostic quizzes for target roles
- [ ] All questions contain valid options, explanations, and difficulty tags
"""
    },
    {
        "title": "Assessment Attempt Scoring & Telemetry Storage",
        "agent": "Database Agent",
        "phase": "Phase 3",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Record student quiz attempts, evaluate objective answers, compute topic percentiles, and persist telemetry.

### Scope & Deliverables
- database/models/assessment_attempt.py: AssessmentAttempt & AssessmentAnswer models
- database/repositories/assessment_repository.py
- Grading engine comparing selected option against question key

### Subagent Owner
Database Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Evaluates 10 submitted MCQ answers deterministically
- [ ] Stores attempt score, total correct, and timestamp in SQLite
"""
    },
    {
        "title": "Deterministic Skill Gap Matrix Engine",
        "agent": "Backend Agent",
        "phase": "Phase 4",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Triangulate student resume skills, target JD requirements, and diagnostic assessment scores to categorize competencies.

### Scope & Deliverables
- services/skill_gap_service.py: Deterministic set logic
- Categorization into Strong Skills, Weak Skills, and Missing Skills
- schemas/skill_gap_schema.py: SkillGapMatrix model

### Subagent Owner
Backend Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Correctly marks high-scoring verified skills as Strong
- [ ] Correctly identifies JD requirements omitted in resume as Missing
- [ ] Ranks priority topics by urgency
"""
    },
    {
        "title": "Adaptive Learning Roadmap Planner Agent",
        "agent": "Foundry Agent",
        "phase": "Phase 5",
        "cost": "Low (<$0.50)",
        "desc": """### Objective
Generate a chronological week-by-week preparation roadmap mapped to student skill gaps and preparation timeline.

### Scope & Deliverables
- agents/planner_agent/planner_agent.py: Foundry agent with structured roadmap prompt
- database/models/learning_plan.py: LearningPlan and LearningPlanItem tables
- schemas/plan_schema.py: Structured plan items (topic, week, priority, practice count)

### Subagent Owner
Foundry Agent

### Azure Cost Impact
Low (<$0.50)

### Acceptance Criteria
- [ ] Produces realistic, chronologically ordered 4-week study plan
- [ ] High-priority gaps scheduled in Week 1 & Week 2
"""
    },
    {
        "title": "RAG Knowledge Base Curation & Chunking Pipeline",
        "agent": "RAG Agent",
        "phase": "Phase 6",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Curate trusted educational guides across 10 placement domains and implement recursive character chunking with metadata tagging.

### Scope & Deliverables
- data/knowledge_base/: High-yield markdown notes for DSA, DBMS, SQL, Java, Python, OOP, OS, CN, ML, Aptitude
- rag/ingestion/chunker.py: Recursive text splitter (800 token target, 120 token overlap)
- Metadata extraction (title, topic, subtopic, section)

### Subagent Owner
RAG Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Splits 10 domain guides into metadata-tagged chunks
- [ ] No chunk exceeds token boundary; zero orphan headings
"""
    },
    {
        "title": "Azure AI Search Index Definition & Ingestion Engine",
        "agent": "RAG Agent",
        "phase": "Phase 6",
        "cost": "Medium (<$5.00)",
        "desc": """### Objective
Define Azure AI Search index schema and build ingestion script with text-embedding-3-small and local fallback mock.

### Scope & Deliverables
- rag/embeddings/azure_embedder.py: Azure OpenAI embedding client + local NumPy cache
- rag/ingestion/indexer.py: Azure AI Search index builder (HNSW vector + BM25 text)
- scripts/ingest_docs.py: Batch upload script

### Subagent Owner
RAG Agent

### Azure Cost Impact
Medium (<$5.00)

### Acceptance Criteria
- [ ] Successfully pushes chunks to Azure AI Search index (or local mock index)
- [ ] Embeddings cached locally to prevent redundant API calls
"""
    },
    {
        "title": "Hybrid Vector & Semantic Retrieval Engine with Citation Generator",
        "agent": "RAG Agent",
        "phase": "Phase 6",
        "cost": "Low (<$1.00)",
        "desc": """### Objective
Execute hybrid search queries (vector similarity + BM25 keyword) and generate strict source citation references.

### Scope & Deliverables
- rag/retrieval/retriever.py: Hybrid search query executor with score threshold (>0.72)
- rag/retrieval/citation_engine.py: Formatter outputting [Source: <title>, Section: <section>]
- tests/unit/test_retrieval.py

### Subagent Owner
RAG Agent

### Azure Cost Impact
Low (<$1.00)

### Acceptance Criteria
- [ ] Returns top-K relevant chunks for technical queries
- [ ] Accurately formats file and section citations
"""
    },
    {
        "title": "RAG Tutor Agent (Grounded Conceptual Assistant)",
        "agent": "RAG Agent",
        "phase": "Phase 6",
        "cost": "Low (<$1.00)",
        "desc": """### Objective
Build conversational tutor agent that answers placement doubts strictly using retrieved knowledge chunks with anti-hallucination guardrails.

### Scope & Deliverables
- agents/tutor_agent/tutor_agent.py: Foundry agent with grounded prompt
- rag/prompts/tutor_prompt.py: System instructions enforcing factual citations
- Rejection handler for queries outside syllabus

### Subagent Owner
RAG Agent

### Azure Cost Impact
Low (<$1.00)

### Acceptance Criteria
- [ ] Answers technical questions with correct markdown citations
- [ ] Rejects out-of-domain queries without hallucinating
"""
    },
    {
        "title": "MCP Student Profile Tool Implementation",
        "agent": "MCP Agent",
        "phase": "Phase 7",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Create FastMCP tool allowing AI agents to query and update student profile parameters through validated schemas.

### Scope & Deliverables
- mcp/tools/profile_tool.py: StudentProfileTool definition
- mcp/server/server.py: FastMCP server registration
- Strict Pydantic input validation and student_id scoping

### Subagent Owner
MCP Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Validates all tool inputs; rejects unauthorized modifications
- [ ] Successfully executes get_profile and update_target actions
"""
    },
    {
        "title": "MCP Progress & Performance Analytics Tool",
        "agent": "MCP Agent",
        "phase": "Phase 7",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Expose student test mastery scores, weakest topics, and question counts as a sandboxed MCP tool.

### Scope & Deliverables
- mcp/tools/progress_tool.py: ProgressPerformanceTool implementation
- Read-only queries against AssessmentAttempt and PracticeAttempt repositories
- tests/unit/test_progress_tool.py

### Subagent Owner
MCP Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Returns structured JSON summary of weakest 3 topics and overall accuracy
"""
    },
    {
        "title": "GitHub MCP Demonstration Tool",
        "agent": "MCP Agent",
        "phase": "Phase 7",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Implement external GitHub MCP tool fetching a candidate's public repositories, star counts, and top programming languages for profile enrichment.

### Scope & Deliverables
- mcp/tools/github_tool.py: GitHub REST API client integration
- Read-only public endpoints with mock fallback when token is omitted
- tests/unit/test_github_tool.py

### Subagent Owner
MCP Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Retrieves top public repositories and language statistics for given GitHub username
"""
    },
    {
        "title": "Microsoft Foundry Master Orchestrator Agent",
        "agent": "Foundry Agent",
        "phase": "Phase 8",
        "cost": "Low (<$2.00)",
        "desc": """### Objective
Implement central Foundry Orchestrator coordinating user intent, maintaining session context, and routing requests to subagents.

### Scope & Deliverables
- agents/orchestrator/orchestrator.py: Master agent loop
- agents/orchestrator/routing_rules.py: Intent classification and subagent delegation
- Bindings to MCP tool server

### Subagent Owner
Foundry Agent

### Azure Cost Impact
Low (<$2.00)

### Acceptance Criteria
- [ ] Accurately routes user prompts to appropriate specialized subagent
- [ ] Maintains conversation history across multiple turns
"""
    },
    {
        "title": "Subagent Swarm Integration & Safety Boundary Checks",
        "agent": "Foundry Agent",
        "phase": "Phase 8",
        "cost": "Low (<$1.00)",
        "desc": """### Objective
Integrate all specialized agents under Orchestrator with timeout handling, rate-limiting guards, and graceful error degradation.

### Scope & Deliverables
- agents/orchestrator/agent_registry.py
- agents/common/error_handler.py: Fallback to cached responses upon network/API limits
- tests/integration/test_orchestrator.py

### Subagent Owner
Foundry Agent

### Azure Cost Impact
Low (<$1.00)

### Acceptance Criteria
- [ ] System remains functional and returns user-friendly messages when external APIs fail
"""
    },
    {
        "title": "Interactive Practice Question & Coding Engine",
        "agent": "Backend Agent",
        "phase": "Phase 9",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Build interactive practice runner presenting MCQs and conceptual coding snippets with instant feedback and telemetry tracking.

### Scope & Deliverables
- database/models/practice.py: PracticeAttempt table
- services/practice_service.py: Practice question fetcher and submission evaluator
- Streak and score calculation

### Subagent Owner
Backend Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Students can solve practice questions, view explanations, and log attempts
"""
    },
    {
        "title": "Performance Evaluation & Mastery Trends Engine",
        "agent": "Evaluation Agent",
        "phase": "Phase 10",
        "cost": "Low (<$0.50)",
        "desc": """### Objective
Aggregate assessment and practice data into topic mastery percentages, learning velocity, and an overall Placement Readiness Index (0-100%).

### Scope & Deliverables
- services/analytics_service.py: Mathematical aggregation functions
- agents/evaluation_agent/evaluation_agent.py: Qualitative performance insights
- schemas/evaluation_schema.py

### Subagent Owner
Evaluation Agent

### Azure Cost Impact
Low (<$0.50)

### Acceptance Criteria
- [ ] Accurately calculates topic mastery % across completed attempts
- [ ] Generates radar chart datasets for UI visualization
"""
    },
    {
        "title": "Next Best Action Recommendation Engine",
        "agent": "Foundry Agent",
        "phase": "Phase 11",
        "cost": "Low (<$0.50)",
        "desc": """### Objective
Implement recommendation engine surfacing 1-3 urgent tactical actions (e.g. 'Revise B-Trees', 'Practice 5 SQL Joins') based on empirical weak spots.

### Scope & Deliverables
- services/next_action_service.py: Rule filter based on lowest topic mastery
- agents/recommendation_agent/recommendation_agent.py: Contextual advice formulation
- database/models/recommendation.py

### Subagent Owner
Foundry Agent

### Azure Cost Impact
Low (<$0.50)

### Acceptance Criteria
- [ ] Recommendations directly reference verified weak areas rather than generic advice
- [ ] Actions link directly to practice and tutor pages
"""
    },
    {
        "title": "Streamlit UI Foundation, Sidebar & Dashboard Pages",
        "agent": "Streamlit UI Agent",
        "phase": "Phase 12",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Construct Streamlit multi-page framework, universal sidebar with student switcher, and master Dashboard.

### Scope & Deliverables
- app/streamlit_app.py: Main entrypoint & session state initialization
- app/pages/1_📊_Dashboard.py: Key metrics, progress rings, current roadmap view
- app/components/sidebar.py: Student selector and quick stats
- Custom CSS styling

### Subagent Owner
Streamlit UI Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Streamlit renders cleanly on localhost:8501
- [ ] Session state persists student selection across pages
"""
    },
    {
        "title": "Complete Streamlit Multi-Page Journey Integration",
        "agent": "Streamlit UI Agent",
        "phase": "Phase 12",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Build and wire remaining 9 Streamlit pages to backend services and Foundry agent orchestrator.

### Scope & Deliverables
- app/pages/2_👤_Student_Profile.py
- app/pages/3_📄_Resume_JD_Analysis.py
- app/pages/4_📝_Diagnostic_Assessment.py
- app/pages/5_🔍_Skill_Gap.py
- app/pages/6_📅_Learning_Plan.py
- app/pages/7_🤖_RAG_Tutor.py
- app/pages/8_💻_Practice.py
- app/pages/9_📈_Performance.py
- app/pages/10_🎯_Next_Best_Action.py

### Subagent Owner
Streamlit UI Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Full 8-stage user journey functions end-to-end without UI crashes
"""
    },
    {
        "title": "Comprehensive Automated Testing Suite",
        "agent": "Testing Agent",
        "phase": "Phase 13",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Implement comprehensive Pytest suite covering unit tests, integration tests, and MCP contract checks.

### Scope & Deliverables
- tests/unit/*: Parsers, services, matrices, models
- tests/integration/*: DB transactions, MCP stdio protocol
- tests/mocks/*: Azure OpenAI and AI Search mock responses
- Code coverage target >80%

### Subagent Owner
Testing Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Entire test suite executes offline with AZURE_MOCK_MODE=True
- [ ] All tests pass in under 15 seconds
"""
    },
    {
        "title": "Security Hardening, Input Sanitization & Secrets Management",
        "agent": "Architecture Agent",
        "phase": "Phase 13",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Harden security: PII sanitization in resume parsing, prompt injection defense, SQL injection prevention, and zero secret leaks.

### Scope & Deliverables
- config/security.py: PII masking and prompt boundary delimiters
- Static security audit ensuring zero committed credentials
- Parameterized ORM queries across all endpoints

### Subagent Owner
Architecture Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Masks sensitive candidate contact details in logs
- [ ] Resists prompt injection test payloads
"""
    },
    {
        "title": "Docker Containerization & Local Dev Shell Scripts",
        "agent": "DevOps Agent",
        "phase": "Phase 14",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Containerize the application for one-command deployment via Docker and Docker Compose.

### Scope & Deliverables
- Dockerfile: Multi-stage Python build
- docker-compose.yml: Service definition with mounted volume for SQLite
- .dockerignore

### Subagent Owner
DevOps Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] `docker compose up` successfully launches app on port 8501
"""
    },
    {
        "title": "Comprehensive Documentation, Demo Script & Project Handover",
        "agent": "DevOps Agent",
        "phase": "Phase 14",
        "cost": "FREE ($0.00)",
        "desc": """### Objective
Author complete setup guides, architecture diagrams, video walkthrough scripts, and deployment instructions.

### Scope & Deliverables
- docs/setup_guide.md: Step-by-step developer installation guide
- docs/demo_walkthrough.md: Structured 5-minute product demonstration script
- Final polish of README.md

### Subagent Owner
DevOps Agent

### Azure Cost Impact
FREE ($0.00)

### Acceptance Criteria
- [ ] Comprehensive documentation verified by a clean clone walkthrough
"""
    }
]

def main():
    print(f"Creating {len(issues)} issues on GitHub repository Jiya-garg08/ai-placement-agent...")
    for idx, item in enumerate(issues, start=1):
        issue_title = f"[#{idx:02d}] {item['title']}"
        labels = f"{item['phase'].lower().replace(' ', '-')},{item['agent'].lower().replace(' ', '-')}"
        
        cmd = [
            "gh", "issue", "create",
            "--title", issue_title,
            "--body", item['desc']
        ]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Created Issue #{idx:02d}: {res.stdout.strip()}")
            time.sleep(0.5) # avoid rate limits
        except subprocess.CalledProcessError as e:
            print(f"Error creating issue #{idx:02d}: {e.stderr}", file=sys.stderr)
            
    print("All GitHub issues created successfully.")

if __name__ == "__main__":
    main()
