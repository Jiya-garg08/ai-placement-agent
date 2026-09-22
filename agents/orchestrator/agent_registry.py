from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from schemas.orchestrator_schema import UserIntent
from agents.resume_agent.resume_agent import ResumeAnalysisAgent
from agents.planner_agent.planner_agent import LearningPlannerAgent
from agents.tutor_agent.tutor_agent import RAGTutorAgent
from services.assessment_service import AssessmentService
from services.skill_gap_service import SkillGapService


@dataclass
class AgentMetadata:
    """Descriptor for a specialized subagent in the Foundry swarm."""
    name: str
    role: str
    description: str
    supported_intents: List[UserIntent]
    timeout_seconds: float = 12.0
    is_mcp_tool: bool = False
    health_status: str = "HEALTHY"  # "HEALTHY", "DEGRADED", "OFFLINE"


class AgentRegistry:
    """Central registry and lifecycle manager for all specialized subagents in the swarm."""

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._intent_map: Dict[UserIntent, str] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Register default specialized agents with their operational constraints."""
        # 1. Resume & Job Description Agent
        self.register(
            AgentMetadata(
                name="ResumeAnalysisAgent",
                role="Resume & JD Evaluation Specialist",
                description="Extracts candidate skills, detects experience seniority, and computes role match scores.",
                supported_intents=[UserIntent.RESUME_ANALYSIS],
                timeout_seconds=15.0
            ),
            instance=ResumeAnalysisAgent(mock_mode=self.mock_mode)
        )

        # 2. Diagnostic Assessment Engine
        self.register(
            AgentMetadata(
                name="AssessmentService",
                role="Diagnostic Testing Specialist",
                description="Manages single-choice technical questions, scores candidate tests, and measures topic accuracy.",
                supported_intents=[UserIntent.DIAGNOSTIC_ASSESSMENT],
                timeout_seconds=10.0
            ),
            instance=AssessmentService()
        )

        # 3. Skill Gap Matrix Service
        self.register(
            AgentMetadata(
                name="SkillGapService",
                role="Competency Triangulation Specialist",
                description="Triangulates resume extracted skills with assessment accuracy to compute Readiness Index.",
                supported_intents=[UserIntent.SKILL_GAP_ANALYSIS],
                timeout_seconds=10.0
            ),
            instance=SkillGapService()
        )

        # 4. Learning Planner Agent
        self.register(
            AgentMetadata(
                name="LearningPlannerAgent",
                role="Adaptive Curriculum Architect",
                description="Generates personalized 4-week preparation roadmaps prioritizing remediation topics.",
                supported_intents=[UserIntent.ROADMAP_PLANNING],
                timeout_seconds=15.0
            ),
            instance=LearningPlannerAgent(mock_mode=self.mock_mode)
        )

        # 5. RAG Pedagogical Tutor
        self.register(
            AgentMetadata(
                name="RAGTutorAgent",
                role="Grounded CS Academic Tutor",
                description="Provides educational explanations with strict citations across 10 core placement subjects.",
                supported_intents=[UserIntent.RAG_TUTOR],
                timeout_seconds=12.0
            ),
            instance=RAGTutorAgent(mock_mode=self.mock_mode)
        )

        # 6. Profile Management MCP Adapter
        self.register(
            AgentMetadata(
                name="ProfileToolAdapter",
                role="Student Profile & Role Specialist",
                description="Manages candidate academic profile, career target roles, and performance telemetry.",
                supported_intents=[UserIntent.PROFILE_MANAGEMENT],
                is_mcp_tool=True,
                timeout_seconds=5.0
            ),
            instance="mcp_profile"
        )

        # 7. GitHub Portfolio MCP Adapter
        self.register(
            AgentMetadata(
                name="GitHubPortfolioAdapter",
                role="GitHub Open Source Inspector",
                description="Inspects candidate public repositories, language distribution, and coding history.",
                supported_intents=[UserIntent.PORTFOLIO_INSPECTION],
                is_mcp_tool=True,
                timeout_seconds=8.0
            ),
            instance="mcp_github"
        )

    def register(self, metadata: AgentMetadata, instance: Any) -> None:
        """Register a subagent with its metadata and executable instance."""
        self._registry[metadata.name] = {
            "metadata": metadata,
            "instance": instance
        }
        for intent in metadata.supported_intents:
            self._intent_map[intent] = metadata.name

    def get_agent_instance(self, agent_name: str) -> Optional[Any]:
        """Fetch executable instance by name."""
        entry = self._registry.get(agent_name)
        return entry["instance"] if entry else None

    def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """Fetch metadata by name."""
        entry = self._registry.get(agent_name)
        return entry["metadata"] if entry else None

    def get_agent_for_intent(self, intent: UserIntent) -> Optional[str]:
        """Find the designated agent name for a given user intent."""
        return self._intent_map.get(intent)

    def list_agents(self) -> List[AgentMetadata]:
        """List all registered agents and their current capabilities."""
        return [entry["metadata"] for entry in self._registry.values()]

    def health_check_all(self) -> Dict[str, str]:
        """Perform system health assessment across all registered swarm subagents."""
        health_report = {}
        for name, entry in self._registry.items():
            meta: AgentMetadata = entry["metadata"]
            health_report[name] = meta.health_status
        return health_report
