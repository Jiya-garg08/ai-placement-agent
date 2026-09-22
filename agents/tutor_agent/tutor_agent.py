from typing import Optional, List, Dict, Any

from config.settings import settings
from schemas.rag_schema import TutorQueryRequest, TutorResponse, CitationSource
from rag.retrieval.retriever import HybridRetriever
from rag.retrieval.citation_engine import CitationEngine
from rag.prompts.tutor_prompt import format_tutor_prompt, RAG_TUTOR_SYSTEM_PROMPT


class RAGTutorAgent:
    """Foundry/Azure OpenAI Conversational Tutor grounded strictly in verified educational material."""

    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        mock_mode: Optional[bool] = None
    ):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.retriever = retriever or HybridRetriever(mock_mode=self.mock_mode)

    def answer_query(self, request: TutorQueryRequest) -> TutorResponse:
        """Process student query, retrieve grounded chunks, and synthesize cited pedagogical explanation."""
        # 1. Retrieve relevant educational chunks
        results = self.retriever.search(
            query=request.query,
            top_k=3,
            topic_filter=request.topic_context,
            min_relevance_score=0.18
        )

        if not results:
            return TutorResponse(
                query=request.query,
                answer=(
                    "I cannot find sufficient verified information on this topic in our placement knowledge base. "
                    "Please ask a question related to core engineering domains: DSA, DBMS, SQL, Java, Python, "
                    "OOP, Operating Systems, Computer Networks, Machine Learning, or Aptitude."
                ),
                citations=[],
                grounded=False
            )

        citations = CitationEngine.extract_citations(results)
        grounded_context = CitationEngine.build_grounded_context(results)

        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            answer = self._heuristic_mock_answer(request.query, results, citations)
        else:
            try:
                answer = self._llm_answer(request.query, grounded_context, request.chat_history, citations, results)
            except Exception:
                answer = self._heuristic_mock_answer(request.query, results, citations)

        return TutorResponse(
            query=request.query,
            answer=answer,
            citations=citations,
            grounded=True
        )

    def _heuristic_mock_answer(self, query: str, results: list, citations: list) -> str:
        """Synthesize high-yield pedagogical answer directly from retrieved chunks for offline usage."""
        top = results[0]
        ref_tag = f"[Source: {top.title}, Section: {top.section}]"

        answer_lines = [
            f"### Conceptual Overview: {top.section}\n",
            f"According to verified curriculum reference {ref_tag}:\n",
            f"{top.content}\n",
            "#### Key Takeaways for Technical Interviews:",
            f"- **Core Principle**: Pay close attention to underlying invariants and edge cases in {top.section}.",
            f"- **Complexity Profile**: Always analyze both runtime time complexity and auxiliary space complexity.",
            CitationEngine.format_citation_markdown(citations)
        ]
        return "\n".join(answer_lines)

    def _llm_answer(self, query: str, grounded_context: str, chat_history: list, citations: list, results: list = None) -> str:
        """Call Azure OpenAI / Foundry model with strict grounded context."""
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        messages = format_tutor_prompt(query, grounded_context, chat_history)
        try:
            resp = client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=messages,
                max_completion_tokens=3500
            )
        except Exception:
            resp = client.chat.completions.create(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=messages,
                temperature=0.2,
                max_tokens=1200
            )
        content = resp.choices[0].message.content or ""
        if not content.strip() and results:
            return self._heuristic_mock_answer(query, results, citations)

        citation_footer = CitationEngine.format_citation_markdown(citations)
        return f"{content}\n{citation_footer}"
