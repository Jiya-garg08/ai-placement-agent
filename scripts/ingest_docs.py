import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.ingestion.chunker import MarkdownDocumentChunker
from rag.ingestion.indexer import RAGIndexer


def run_ingestion():
    kb_dir = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
    print(f"Reading placement preparation guides from {kb_dir}...")

    chunker = MarkdownDocumentChunker(target_chunk_size=800, chunk_overlap=120)
    chunks = chunker.chunk_directory(kb_dir)
    print(f"Extracted {len(chunks)} knowledge chunks across domains.")

    indexer = RAGIndexer()
    total = indexer.index_chunks(chunks)
    print(f"Successfully embedded and indexed {total} chunks in search index.")


if __name__ == "__main__":
    run_ingestion()
