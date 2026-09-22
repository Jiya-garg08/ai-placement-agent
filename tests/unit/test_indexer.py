import pytest
from pathlib import Path
from rag.embeddings.azure_embedder import AzureEmbedder, EMBEDDING_DIM
from rag.ingestion.chunker import MarkdownDocumentChunker
from rag.ingestion.indexer import RAGIndexer
from schemas.rag_schema import KnowledgeChunk


def test_azure_embedder_mock():
    embedder = AzureEmbedder(mock_mode=True)
    vec = embedder.get_embedding("Binary Search Trees and Big-O Complexity")

    assert len(vec) == EMBEDDING_DIM
    # Check that identical string retrieves cached vector
    vec2 = embedder.get_embedding("Binary Search Trees and Big-O Complexity")
    assert vec == vec2


def test_rag_indexer_local_store():
    embedder = AzureEmbedder(mock_mode=True)
    indexer = RAGIndexer(embedder=embedder, mock_mode=True)

    test_chunk = KnowledgeChunk(
        id="test-chunk-1",
        title="Test Domain",
        topic="Testing",
        subtopic="Mocking",
        section="Overview",
        content="Testing the RAG indexing pipeline locally with zero Azure spend.",
        token_count=15,
        source_file="test.md"
    )

    count = indexer.index_chunks([test_chunk])
    assert count == 1
    assert indexer.get_total_indexed() >= 1


def test_full_knowledge_base_indexing():
    kb_dir = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"
    chunker = MarkdownDocumentChunker()
    chunks = chunker.chunk_directory(kb_dir)

    indexer = RAGIndexer(mock_mode=True)
    indexed_count = indexer.index_chunks(chunks)

    assert indexed_count >= 20
    assert indexer.get_total_indexed() >= 20
