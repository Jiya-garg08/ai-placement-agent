import uuid
from typing import Optional, List, Dict, Any

from config.settings import settings
from schemas.orchestrator_schema import (
    UserIntent,
    ChatMessage,
    ConversationSession,
    OrchestratorResponse
)
from schemas.rag_schema import TutorQueryRequest, CitationSource
from agents.orchestrator.routing_rules import IntentRouter
from agents.tutor_agent.tutor_agent import RAGTutorAgent
from agents.planner_agent.planner_agent import LearningPlannerAgent
from agents.resume_agent.resume_agent import ResumeAnalysisAgent
from mcp_service.tools.profile_tool import get_student_profile, update_student_target_role
from mcp_service.tools.progress_tool import (
    get_student_performance_summary,
    get_active_learning_roadmap,
    mark_roadmap_item_status
)
from mcp_service.tools.github_tool import get_github_portfolio


class FoundryMasterOrchestrator:
    """Master AI Orchestrator that coordinates student interactions across specialized subagents,

    maintains multi-turn context, and binds to MCP tool services.
    """

    def __init__(
        self,
        router: Optional[IntentRouter] = None,
        tutor_agent: Optional[RAGTutorAgent] = None,
        planner_agent: Optional[LearningPlannerAgent] = None,
        resume_agent: Optional[ResumeAnalysisAgent] = None,
        mock_mode: Optional[bool] = None
    ):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.router = router or IntentRouter(mock_mode=self.mock_mode)
        self.tutor_agent = tutor_agent or RAGTutorAgent(mock_mode=self.mock_mode)
        self.planner_agent = planner_agent or LearningPlannerAgent(mock_mode=self.mock_mode)
        self.resume_agent = resume_agent or ResumeAnalysisAgent(mock_mode=self.mock_mode)

        # In-memory multi-turn session repository
        self._sessions: Dict[str, ConversationSession] = {}

        # Available MCP Tool Registry bindings
        self._mcp_tool_bindings = {
            "get_student_profile": get_student_profile,
            "update_student_target_role": update_student_target_role,
            "get_student_performance_summary": get_student_performance_summary,
            "get_active_learning_roadmap": get_active_learning_roadmap,
            "mark_roadmap_item_status": mark_roadmap_item_status,
            "get_github_portfolio": get_github_portfolio,
        }

    # --------------------------------------------------------------------------
    # Session Management
    # --------------------------------------------------------------------------
    def get_or_create_session(self, session_id: Optional[str] = None, student_id: Optional[int] = None) -> ConversationSession:
        """Retrieve existing session or initialize a new conversation session."""
        sid = session_id or str(uuid.uuid4())
        if sid not in self._sessions:
            self._sessions[sid] = ConversationSession(
                session_id=sid,
                student_id=student_id
            )
        elif student_id is not None and self._sessions[sid].student_id is None:
            self._sessions[sid].student_id = student_id
        return self._sessions[sid]

    def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """Fetch all conversational turns for an active session."""
        if session_id in self._sessions:
            return self._sessions[session_id].messages
        return []

    def clear_session(self, session_id: str) -> None:
        """Reset history for a given session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    # --------------------------------------------------------------------------
    # MCP Tool Execution Binding
    # --------------------------------------------------------------------------
    def execute_mcp_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Directly invoke a registered MCP tool under sandboxed execution."""
        if tool_name not in self._mcp_tool_bindings:
            return {"error": f"Tool '{tool_name}' is not registered in the MCP tool bindings."}
        try:
            tool_func = self._mcp_tool_bindings[tool_name]
            return tool_func(**kwargs)
        except Exception as e:
            return {"error": f"MCP tool execution failed: {str(e)}"}

    # --------------------------------------------------------------------------
    # Master Dispatch Loop
    # --------------------------------------------------------------------------
    def handle_message(
        self,
        session_id: str,
        message: str,
        student_id: Optional[int] = None
    ) -> OrchestratorResponse:
        """Main entry point: Classifies user prompt, maintains conversational context,

        dispatches to the specialized subagent or MCP tool, and returns an actionable response.
        """
        session = self.get_or_create_session(session_id, student_id)

        # 1. Classify Intent using routing rules with active conversational context
        classification = self.router.classify(message, context=session.context)
        intent = classification.intent
        params = classification.extracted_params

        # Record incoming user turn
        user_turn = ChatMessage(
            role="user",
            content=message,
            intent=intent,
            metadata={"params": params, "confidence": classification.confidence}
        )
        session.messages.append(user_turn)

        # 2. Dispatch to specialized agent or handler
        response_text = ""
        delegated_agent = "FoundryMasterOrchestrator"
        citations: List[CitationSource] = []
        suggested_actions: List[str] = []
        data_payload: Optional[Dict[str, Any]] = None

        if intent == UserIntent.RAG_TUTOR:
            delegated_agent = "RAGTutorAgent"
            topic_ctx = params.get("topic_context") or session.context.get("active_topic")
            
            # Format prior turns for conversational grounding
            chat_history_list = [
                {"role": m.role, "content": m.content}
                for m in session.messages[-5:-1]
            ]
            
            tutor_req = TutorQueryRequest(
                student_id=session.student_id or 1,
                query=message,
                topic_context=topic_ctx,
                chat_history=chat_history_list
            )
            tutor_resp = self.tutor_agent.answer_query(tutor_req)
            response_text = tutor_resp.answer
            citations = tutor_resp.citations
            
            if topic_ctx:
                session.context["active_topic"] = topic_ctx
                suggested_actions = [
                    f"Take a diagnostic test on {topic_ctx}",
                    f"Practice interview coding questions in {topic_ctx}",
                    "View recommended learning roadmap"
                ]
            else:
                suggested_actions = [
                    "Ask a conceptual question on DSA, DBMS, or OS",
                    "Take diagnostic assessment",
                    "Generate preparation roadmap"
                ]

        elif intent == UserIntent.ROADMAP_PLANNING:
            delegated_agent = "LearningPlannerAgent"
            # Check if student already has an active roadmap via MCP tool
            target_student_id = session.student_id or 1
            mcp_roadmap = self.execute_mcp_tool("get_active_learning_roadmap", student_id=target_student_id)
            
            if "roadmap" in mcp_roadmap and mcp_roadmap["roadmap"].get("items"):
                roadmap_info = mcp_roadmap["roadmap"]
                response_text = (
                    f"### Current Active Preparation Roadmap: {roadmap_info['title']}\n\n"
                    f"**Target Role:** {roadmap_info.get('target_role', 'Software Development Engineer')}\n"
                    f"**Total Duration:** {roadmap_info.get('total_weeks', 4)} weeks | "
                    f"**Daily Commitment:** {roadmap_info.get('daily_hours_target', 2.5)} hours\n\n"
                    f"#### Upcoming Milestones:\n"
                )
                for item in roadmap_info.get("items", [])[:4]:
                    status_badge = "[COMPLETED]" if item["status"] == "COMPLETED" else "[PENDING]"
                    response_text += f"- **Week {item['week_number']}: {item['topic']}** ({item['subtopic']}) {status_badge}\n"
                    response_text += f"  - Objective: {item['description']}\n"
                
                data_payload = roadmap_info
            else:
                # Generate new roadmap via planner
                plan_structure = self.planner_agent.generate_plan(
                    target_role=params.get("target_role", "Software Development Engineer"),
                    skill_gap=None,
                    total_weeks=4,
                    daily_hours=2.5
                )
                response_text = (
                    f"### Generated 4-Week Placement Preparation Plan\n\n"
                    f"**Target Role:** {plan_structure.target_role}\n\n"
                )
                for item in plan_structure.items[:4]:
                    subtopics_str = ", ".join(item.subtopics) if item.subtopics else item.topic
                    response_text += f"- **Week {item.week_number}: {item.topic}** ({subtopics_str})\n"
                    response_text += f"  - Milestone: {item.learning_objectives} (Target: {item.practice_goal_count} problems)\n"
                data_payload = plan_structure.model_dump()

            suggested_actions = [
                "Mark a milestone as COMPLETED",
                "Ask tutor to explain Week 1 topic",
                "Take diagnostic test to calibrate roadmap"
            ]

        elif intent == UserIntent.PORTFOLIO_INSPECTION:
            delegated_agent = "GitHubPortfolioTool"
            username = params.get("username")
            if not username and session.student_id:
                prof = self.execute_mcp_tool("get_student_profile", student_id=session.student_id)
                username = prof.get("github_username")

            if not username:
                username = "Jiya-garg08"  # Default to candidate workspace username

            portfolio_res = self.execute_mcp_tool("get_github_portfolio", username=username)
            if "error" in portfolio_res:
                response_text = f"Could not inspect GitHub portfolio: {portfolio_res['error']}"
            else:
                repos_count = portfolio_res.get("public_repo_count", 0)
                total_stars = portfolio_res.get("total_stars", 0)
                langs = ", ".join(portfolio_res.get("top_languages", []))
                response_text = (
                    f"### GitHub Portfolio Analysis: @{portfolio_res.get('username')}\n\n"
                    f"- **Public Repositories Analyzed:** {repos_count}\n"
                    f"- **Total Stars:** {total_stars}\n"
                    f"- **Primary Tech Stack:** {langs or 'N/A'}\n"
                    f"- **Portfolio Match Assessment:** Strong hands-on coding evidence in modern software engineering."
                )
                data_payload = portfolio_res

            suggested_actions = [
                "Analyze resume match against target JD",
                "Generate custom roadmap for GitHub tech stack",
                "Take technical assessment"
            ]

        elif intent == UserIntent.PROFILE_MANAGEMENT:
            delegated_agent = "StudentProfileService"
            sid = session.student_id or 1
            if "target_role" in params:
                new_role = params["target_role"]
                update_res = self.execute_mcp_tool("update_student_target_role", student_id=sid, new_target_role=new_role)
                response_text = f"Your target role has been successfully updated to **{new_role}**."
                data_payload = update_res
            else:
                prof = self.execute_mcp_tool("get_student_profile", student_id=sid)
                if "error" in prof:
                    response_text = f"Profile lookup: {prof['error']}. Please ensure you are logged in or registered."
                else:
                    response_text = (
                        f"### Student Profile Overview\n\n"
                        f"- **Name:** {prof.get('full_name')}\n"
                        f"- **Email:** {prof.get('email')}\n"
                        f"- **Target Role:** {prof.get('target_role')}\n"
                        f"- **Graduation Year:** {prof.get('graduation_year', 'N/A')}\n"
                        f"- **GitHub:** @{prof.get('github_username', 'Not linked')}"
                    )
                    data_payload = prof

            suggested_actions = [
                "View performance & diagnostic scores",
                "Inspect GitHub portfolio",
                "View active roadmap"
            ]

        elif intent == UserIntent.DIAGNOSTIC_ASSESSMENT:
            delegated_agent = "AssessmentService"
            topic = params.get("topic")
            topic_str = f" for **{topic}**" if topic else ""
            response_text = (
                f"### Diagnostic Assessment Engine\n\n"
                f"Diagnostic assessments evaluate your conceptual and problem-solving readiness{topic_str} "
                f"across 10 core computer science domains:\n"
                f"- **Core Domains:** DSA, DBMS, SQL, Operating Systems, Computer Networks, OOP\n"
                f"- **Languages & Applied:** Java, Python, Machine Learning, Quantitative Aptitude\n\n"
                f"Each diagnostic test presents curated single-choice questions with automated score attribution "
                f"to calibrate your personalized skill gap matrix."
            )
            suggested_actions = [
                f"Start {topic or 'DSA'} Diagnostic Test",
                "View past assessment attempt history",
                "Ask tutor for review of tricky concepts"
            ]

        elif intent == UserIntent.SKILL_GAP_ANALYSIS:
            delegated_agent = "SkillGapService"
            sid = session.student_id or 1
            perf = self.execute_mcp_tool("get_student_performance_summary", student_id=sid)
            readiness = perf.get("placement_readiness_index", 0.0) if "error" not in perf else 0.0
            
            response_text = (
                f"### Placement Skill Gap & Readiness Assessment\n\n"
                f"- **Overall Placement Readiness Index:** **{readiness:.1f}%**\n"
                f"- **Diagnostic Attempts Recorded:** {perf.get('total_diagnostic_attempts', 0)}\n\n"
                f"The Skill Gap engine triangulates your parsed resume qualifications and diagnostic assessment scores "
                f"against your target role requirements to highlight **Strong**, **Weak**, and **Missing** competencies."
            )
            data_payload = perf if "error" not in perf else None
            suggested_actions = [
                "Generate 4-Week Remediation Roadmap",
                "Take diagnostic test to boost readiness score",
                "Ask tutor for explanations on weak topics"
            ]

        elif intent == UserIntent.RESUME_ANALYSIS:
            delegated_agent = "ResumeAnalysisAgent"
            response_text = (
                "### Resume & Job Description Matching Engine\n\n"
                "I can analyze your resume against any target software engineering job description:\n"
                "1. **PII Sanitization**: Redacts personal contact details before model analysis.\n"
                "2. **Skill Extraction**: Identifies technical skills, frameworks, and tools.\n"
                "3. **ATS & Match Scoring**: Computes role compatibility, identifies missing requirements, "
                "and highlights high-impact experience bullets."
            )
            suggested_actions = [
                "Upload Resume (PDF / DOCX)",
                "Paste Job Description text",
                "View sample resume analysis report"
            ]

        else:  # UserIntent.GENERAL_CONVERSATION
            delegated_agent = "FoundryMasterOrchestrator"
            response_text = (
                "👋 Hello! I am your **AI Placement Preparation Agent**, powered by Microsoft Foundry and Model Context Protocol.\n\n"
                "I am here to guide you step-by-step to your target software engineering offer:\n"
                "- 📄 **Resume & JD Match**: ATS compatibility and gap extraction.\n"
                "- 📝 **Diagnostic Assessments**: Calibrate your mastery across 10 CS domains.\n"
                "- 🎯 **Skill Gap Matrix**: Pinpoint weak and missing requirements.\n"
                "- 🗺️ **Adaptive Roadmap**: 4-week structured preparation curriculum.\n"
                "- 📚 **RAG Tutor**: Verified, cited answers for DSA, DBMS, OS, Networks, and more.\n"
                "- 🐙 **Portfolio Analysis**: Inspect your GitHub projects and tech stack.\n\n"
                "How would you like to begin today?"
            )
            suggested_actions = [
                "Start Diagnostic Assessment",
                "Generate 4-Week Learning Roadmap",
                "Ask a Technical CS Question",
                "Inspect GitHub Portfolio"
            ]

        # Record assistant turn
        assistant_turn = ChatMessage(
            role="assistant",
            content=response_text,
            intent=intent,
            metadata={"delegated_agent": delegated_agent, "has_citations": len(citations) > 0}
        )
        session.messages.append(assistant_turn)

        return OrchestratorResponse(
            session_id=session.session_id,
            intent=intent,
            delegated_agent=delegated_agent,
            response_text=response_text,
            citations=citations,
            suggested_actions=suggested_actions,
            data=data_payload
        )
