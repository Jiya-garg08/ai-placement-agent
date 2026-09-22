import re
from typing import Optional, Dict, Any, Tuple
from config.settings import settings
from schemas.orchestrator_schema import UserIntent, IntentClassificationResult

# Technical domain keywords mapped to knowledge base topic filters
TOPIC_KEYWORDS = {
    "DSA": [
        "dsa", "data structure", "data structures", "algorithm", "algorithms",
        "binary tree", "binary search tree", "bst", "graph", "graphs",
        "linked list", "linked lists", "array", "arrays", "stack", "queue",
        "dynamic programming", "dp", "time complexity", "space complexity",
        "search complexity", "big o", "sorting", "searching", "heap", "trie",
        "recursion", "tree", "trees"
    ],
    "DBMS": [
        "dbms", "database", "acid", "transaction", "isolation", "normalization",
        "1nf", "2nf", "3nf", "bcnf", "b-tree", "b+ tree", "concurrency control",
        "indexing", "rdbms"
    ],
    "SQL": [
        "sql", "select", "query", "group by", "having", "inner join", "left join",
        "outer join", "subquery", "aggregate", "window function", "cte"
    ],
    "Operating Systems": [
        "operating system", "os", "process", "thread", "deadlock", "mutex",
        "semaphore", "paging", "virtual memory", "context switch", "cpu scheduling",
        "banker's algorithm", "thrashing"
    ],
    "Computer Networks": [
        "computer network", "networking", "tcp", "udp", "osi model", "ip address",
        "dns", "http", "https", "socket", "three-way handshake", "congestion control",
        "subnet", "router"
    ],
    "OOP": [
        "oop", "object oriented", "inheritance", "polymorphism", "encapsulation",
        "abstraction", "solid principles", "interface", "design pattern"
    ],
    "Java": [
        "java", "jvm", "jre", "jdk", "garbage collection", "hashmap", "string pool",
        "concurrenthashmap", "generics", "multithreading java"
    ],
    "Python": [
        "python", "gil", "global interpreter lock", "generator", "decorator",
        "lambda", "list comprehension", "dunder", "asyncio"
    ],
    "Machine Learning": [
        "machine learning", "ml", "linear regression", "logistic regression",
        "gradient descent", "overfitting", "underfitting", "precision", "recall",
        "roc", "auc", "neural network"
    ],
    "Aptitude": [
        "aptitude", "probability", "permutation", "combination", "time and work",
        "speed distance", "percentage", "profit loss", "ratio"
    ]
}

CANONICAL_TOPIC_MAP = {
    "DSA": "Data Structures and Algorithms",
    "DBMS": "Database Management Systems",
    "SQL": "Structured Query Language (SQL)",
    "Operating Systems": "Operating Systems",
    "Computer Networks": "Computer Networks",
    "OOP": "Object-Oriented Programming (OOP)",
    "Java": "Java Programming",
    "Python": "Python Programming",
    "Machine Learning": "Machine Learning",
    "Aptitude": "Aptitude and Quantitative Reasoning"
}


class IntentRouter:
    """Classifies user queries into discrete agent capabilities and extracts relevant parameters."""

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE

    def classify(self, message: str, context: Optional[Dict[str, Any]] = None) -> IntentClassificationResult:
        """Determine target intent and extracted arguments from user message."""
        clean_msg = message.strip()
        lower_msg = clean_msg.lower()

        # If live Azure OpenAI credentials available and not mock mode, use structured LLM classification
        if not self.mock_mode and settings.AZURE_OPENAI_API_KEY:
            try:
                return self._llm_classify(clean_msg, context)
            except Exception:
                # Fall back to heuristic classification on any network/API exception
                pass

        return self._heuristic_classify(clean_msg, lower_msg, context)

    def _heuristic_classify(
        self,
        clean_msg: str,
        lower_msg: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentClassificationResult:
        """Deterministic heuristic rule-based intent router with zero token cost."""
        params: Dict[str, Any] = {}

        # 1. GitHub Portfolio Inspection
        if "github" in lower_msg or "portfolio" in lower_msg or "repositories" in lower_msg:
            # Extract username if provided: "github.com/username" or "github user: username" or "username github"
            gh_match = re.search(r"github\.com/([a-zA-Z0-9_\-]+)", clean_msg, re.IGNORECASE)
            if not gh_match:
                gh_match = re.search(r"(?:user(?:name)?|profile|account)\s*[:=]?\s*([a-zA-Z0-9_\-]+)", clean_msg, re.IGNORECASE)
            if not gh_match:
                # E.g. "inspect Jiya-garg08 on github"
                gh_match = re.search(r"([a-zA-Z0-9_\-]+)\s*(?:'s)?\s*github", clean_msg, re.IGNORECASE)
            
            if gh_match:
                params["username"] = gh_match.group(1).strip()

            return IntentClassificationResult(
                intent=UserIntent.PORTFOLIO_INSPECTION,
                confidence=0.95,
                extracted_params=params,
                reasoning="Identified GitHub portfolio analysis keywords."
            )

        # 2. Resume & Job Description Analysis
        resume_keywords = ["resume", "cv", "job description", "target jd", "ats score", "match score", "parse resume"]
        if any(kw in lower_msg for kw in resume_keywords):
            return IntentClassificationResult(
                intent=UserIntent.RESUME_ANALYSIS,
                confidence=0.92,
                extracted_params=params,
                reasoning="Identified resume or job description analysis keywords."
            )

        # 3. Diagnostic Assessment
        assessment_keywords = ["diagnostic", "take test", "start test", "quiz", "assessment", "sample questions", "evaluate my skills", "mock test", "exam"]
        if any(kw in lower_msg for kw in assessment_keywords):
            topic = self._extract_topic(lower_msg)
            if topic:
                params["topic"] = topic
            return IntentClassificationResult(
                intent=UserIntent.DIAGNOSTIC_ASSESSMENT,
                confidence=0.90,
                extracted_params=params,
                reasoning="Identified assessment/diagnostic examination keywords."
            )

        # 3b. Interactive Practice Questions & Coding Drills
        practice_keywords = ["practice question", "practice problem", "coding question", "solve problem", "coding challenge", "practice mcq", "code snippet", "practice dsa", "coding drill"]
        if any(kw in lower_msg for kw in practice_keywords) or (lower_msg.startswith("practice") and "plan" not in lower_msg):
            topic = self._extract_topic(lower_msg)
            if topic:
                params["topic"] = topic
            return IntentClassificationResult(
                intent=UserIntent.PRACTICE_DRILL,
                confidence=0.91,
                extracted_params=params,
                reasoning="Identified interactive practice or coding drill keywords."
            )

        # 4. Skill Gap Matrix
        skill_gap_keywords = ["skill gap", "missing skill", "weak skill", "strong skill", "readiness index", "gap matrix", "where am i lacking", "what should i improve", "skill deficiency"]
        if any(kw in lower_msg for kw in skill_gap_keywords):
            return IntentClassificationResult(
                intent=UserIntent.SKILL_GAP_ANALYSIS,
                confidence=0.90,
                extracted_params=params,
                reasoning="Identified skill gap and readiness assessment keywords."
            )

        # 5. Roadmap & Preparation Planning
        roadmap_keywords = ["roadmap", "study plan", "learning plan", "curriculum", "preparation schedule", "create plan", "4-week", "study schedule", "learning milestone"]
        if any(kw in lower_msg for kw in roadmap_keywords):
            return IntentClassificationResult(
                intent=UserIntent.ROADMAP_PLANNING,
                confidence=0.92,
                extracted_params=params,
                reasoning="Identified roadmap planning or curriculum generation keywords."
            )

        # 6. Profile Management
        profile_keywords = ["my profile", "update profile", "change target role", "target role", "student profile", "student info", "performance summary", "my progress"]
        if any(kw in lower_msg for kw in profile_keywords):
            # Check for role update pattern
            role_match = re.search(r"(?:change|update|set)\s*(?:target\s*)?role\s*(?:to|as)?\s*([a-zA-Z\s]+)", clean_msg, re.IGNORECASE)
            if role_match:
                params["target_role"] = role_match.group(1).strip()

            return IntentClassificationResult(
                intent=UserIntent.PROFILE_MANAGEMENT,
                confidence=0.88,
                extracted_params=params,
                reasoning="Identified student profile or performance summary request."
            )

        # 7. RAG Technical Tutor (Domain-specific technical question or concept explanation)
        topic = self._extract_topic(lower_msg)
        tutor_indicators = ["what is", "how does", "explain", "difference between", "how to", "why is", "complexity", "code for", "implement", "example of"]
        is_tutor_pattern = any(ind in lower_msg for ind in tutor_indicators)

        if topic or is_tutor_pattern:
            if topic:
                params["topic_context"] = topic
            elif context and context.get("active_topic"):
                params["topic_context"] = context["active_topic"]

            return IntentClassificationResult(
                intent=UserIntent.RAG_TUTOR,
                confidence=0.85 if topic else 0.70,
                extracted_params=params,
                reasoning=f"Identified technical educational question in domain: {topic or 'general'}."
            )

        # 8. General Conversation / Greeting / Help
        return IntentClassificationResult(
            intent=UserIntent.GENERAL_CONVERSATION,
            confidence=0.80,
            extracted_params=params,
            reasoning="Fallback to general placement preparation conversational guidance."
        )

    def _extract_topic(self, text: str) -> Optional[str]:
        """Match technical keywords against canonical placement domains."""
        for domain, keywords in TOPIC_KEYWORDS.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", text):
                    return CANONICAL_TOPIC_MAP.get(domain, domain)
        return None

    def _llm_classify(self, message: str, context: Optional[Dict[str, Any]]) -> IntentClassificationResult:
        """Call Azure OpenAI / Foundry model for semantic intent routing."""
        from openai import AzureOpenAI
        import json

        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        prompt = f"""You are an intent classification engine for an AI Placement Preparation Agent.
Analyze the user message and classify it into one of the following intents:
- resume_analysis: Questions or requests about resume parsing, job descriptions, or resume matching.
- diagnostic_assessment: Requests to take tests, quizzes, or view assessment questions.
- skill_gap_analysis: Inquiries about skill gaps, missing skills, or readiness scores.
- roadmap_planning: Requests to generate, view, or update preparation study plans/roadmaps.
- rag_tutor: Educational, technical, or conceptual questions on computer science topics.
- profile_management: Inquiries or updates to candidate profile, target role, or progress summary.
- portfolio_inspection: Requests to inspect or view GitHub repositories/portfolio.
- general_conversation: Greetings, platform questions, general help.

Context: {json.dumps(context or {})}
User message: "{message}"
"""
        response = client.beta.chat.completions.parse(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a precise intent classification agent. Return valid structured output."},
                {"role": "user", "content": prompt}
            ],
            response_format=IntentClassificationResult,
            temperature=0.0
        )
        return response.choices[0].message.parsed
