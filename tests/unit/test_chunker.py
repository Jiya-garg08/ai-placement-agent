from pathlib import Path
import pytest

from rag.ingestion.chunker import MarkdownDocumentChunker
from schemas.rag_schema import KnowledgeChunk

SAMPLE_MD = """# Database Systems

## Normalization Overview
Normalization is the process of structuring relational database relations to minimize data redundancy and prevent update anomalies.

## Boyce-Codd Normal Form
BCNF is a strict version of 3NF where every determinant must be a candidate key. This prevents redundancy resulting from functional dependencies.
"""


def test_markdown_chunker_basic():
    chunker = MarkdownDocumentChunker(target_chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_markdown_text(SAMPLE_MD, "dbms_test.md")

    assert len(chunks) == 2
    c1, c2 = chunks[0], chunks[1]

    assert c1.title == "Database Systems"
    assert c1.section == "Normalization Overview"
    assert "update anomalies" in c1.content
    assert c1.source_file == "dbms_test.md"

    assert c2.section == "Boyce-Codd Normal Form"
    assert "BCNF" in c2.content


def test_chunk_entire_knowledge_base_directory():
    kb_dir = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"
    assert kb_dir.exists()

    chunker = MarkdownDocumentChunker()
    chunks = chunker.chunk_directory(kb_dir)

    # We created 10 markdown files, each with multiple sections
    assert len(chunks) >= 20
    
    # Check that core domains exist among chunks
    topics = set(c.title for c in chunks)
    assert any("Data Structures" in t for t in topics)
    assert any("Database" in t for t in topics)
    assert any("Operating Systems" in t for t in topics)
    assert any("Computer Networks" in t for t in topics)
    assert any("Python" in t for t in topics)

    for chunk in chunks:
        assert isinstance(chunk, KnowledgeChunk)
        assert chunk.token_count > 0
        assert len(chunk.content) > 10
        assert chunk.id.strip() != ""
