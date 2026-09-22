from typing import List, Tuple
from schemas.rag_schema import SearchResultItem, CitationSource


class CitationEngine:
    """Formats retrieved document chunks into context prompts with explicit source citations."""

    @staticmethod
    def build_grounded_context(results: List[SearchResultItem]) -> str:
        """Construct a structured context block with reference tags for LLM ingestion."""
        if not results:
            return "No verified reference documents found in knowledge base."

        context_blocks = []
        for idx, r in enumerate(results, start=1):
            block = f"""[Document {idx}]
Title: {r.title}
Section: {r.section}
Source File: {r.source_file}
Content:
{r.content}
"""
            context_blocks.append(block)

        return "\n---------------------\n".join(context_blocks)

    @staticmethod
    def extract_citations(results: List[SearchResultItem]) -> List[CitationSource]:
        """Transform search results into structured CitationSource objects."""
        citations = []
        seen = set()

        for r in results:
            key = (r.title, r.section)
            if key not in seen:
                seen.add(key)
                citations.append(CitationSource(
                    title=r.title,
                    section=r.section,
                    source_file=r.source_file,
                    relevance_score=round(r.score, 3)
                ))

        return citations

    @staticmethod
    def format_citation_markdown(citations: List[CitationSource]) -> str:
        """Format a list of citations into a clean Markdown reference block for the UI."""
        if not citations:
            return ""

        lines = ["\n\n**📚 References & Verified Sources:**"]
        for c in citations:
            lines.append(f"- *{c.title}* — **{c.section}** (`{c.source_file}`)")
        return "\n".join(lines)
