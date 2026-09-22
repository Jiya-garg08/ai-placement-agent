import pytest
from rag.retrieval.retriever import HybridRetriever
from rag.retrieval.citation_engine import CitationEngine
from schemas.rag_schema import SearchResultItem


def test_hybrid_retriever_local():
    retriever = HybridRetriever(mock_mode=True)
    results = retriever.search("Boyce-Codd Normal Form and super key", top_k=3)

    assert len(results) >= 1
    top = results[0]
    assert isinstance(top, SearchResultItem)
    assert "Database" in top.title or "Normalization" in top.section or "BCNF" in top.content


def test_retriever_dsa_query():
    retriever = HybridRetriever(mock_mode=True)
    results = retriever.search("Binary Search Tree time complexity", top_k=2)

    assert len(results) >= 1
    # One of the results should be from DSA
    assert any("Data Structures" in r.title for r in results)


def test_citation_engine_formatting():
    mock_results = [
        SearchResultItem(
            id="test-1",
            title="Database Management Systems",
            topic="DBMS",
            section="Normalization and Normal Forms",
            content="BCNF requires that every determinant is a super key.",
            source_file="dbms.md",
            score=0.89
        ),
        SearchResultItem(
            id="test-2",
            title="Operating Systems",
            topic="OS",
            section="Deadlocks and Coffman Conditions",
            content="Coffman conditions include mutual exclusion.",
            source_file="operating_systems.md",
            score=0.75
        )
    ]

    context = CitationEngine.build_grounded_context(mock_results)
    assert "[Document 1]" in context
    assert "Database Management Systems" in context
    assert "[Document 2]" in context

    citations = CitationEngine.extract_citations(mock_results)
    assert len(citations) == 2
    assert citations[0].title == "Database Management Systems"
    assert citations[0].section == "Normalization and Normal Forms"

    md = CitationEngine.format_citation_markdown(citations)
    assert "**📚 References & Verified Sources:**" in md
    assert "dbms.md" in md
