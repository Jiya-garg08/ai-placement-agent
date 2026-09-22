import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from config.settings import settings
from schemas.rag_schema import KnowledgeChunk
from rag.embeddings.azure_embedder import AzureEmbedder

LOCAL_INDEX_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "local_search_index.json"


class RAGIndexer:
    """Manages Azure AI Search index lifecycle and local mock vector index persistence."""

    def __init__(self, embedder: Optional[AzureEmbedder] = None, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.embedder = embedder or AzureEmbedder(mock_mode=self.mock_mode)
        self.local_index: List[Dict[str, Any]] = self._load_local_index()

    def _load_local_index(self) -> List[Dict[str, Any]]:
        """Load offline vector index from disk."""
        if LOCAL_INDEX_FILE.exists():
            try:
                with open(LOCAL_INDEX_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_local_index(self):
        """Save offline vector index to disk."""
        try:
            LOCAL_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOCAL_INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_index, f)
        except Exception:
            pass

    def create_or_update_index(self):
        """Initialize Azure AI Search index schema if live Azure credentials are provided."""
        if self.mock_mode or not settings.AZURE_SEARCH_API_KEY:
            # Local mock index requires no remote provisioning
            return

        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents.indexes import SearchIndexClient
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SimpleField,
                SearchableField,
                SearchField,
                SearchFieldDataType,
                VectorSearch,
                HnswAlgorithmConfiguration,
                VectorSearchProfile
            )

            credential = AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
            client = SearchIndexClient(endpoint=settings.AZURE_SEARCH_SERVICE_ENDPOINT, credential=credential)

            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
                SearchableField(name="title", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="topic", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="subtopic", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="section", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="hnsw-profile"
                )
            ]

            vector_search = VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
                profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo")]
            )

            index = SearchIndex(name=settings.AZURE_SEARCH_INDEX_NAME, fields=fields, vector_search=vector_search)
            client.create_or_update_index(index)
        except Exception as e:
            # Log and fall back to local indexing
            print(f"[RAGIndexer] Azure index setup warning: {e}. Utilizing local index fallback.")

    def index_chunks(self, chunks: List[KnowledgeChunk]) -> int:
        """Embed text chunks and persist them to Azure AI Search and/or local index."""
        self.create_or_update_index()
        indexed_docs = []

        for c in chunks:
            vector = self.embedder.get_embedding(c.content)
            doc = {
                "id": c.id.replace("_", "-").replace(" ", "-"),
                "title": c.title,
                "topic": c.topic,
                "subtopic": c.subtopic or "",
                "section": c.section,
                "content": c.content,
                "source_file": c.source_file,
                "content_vector": vector
            }
            indexed_docs.append(doc)

        # Update local index (avoid duplicate IDs)
        existing_ids = {d["id"] for d in self.local_index}
        for doc in indexed_docs:
            if doc["id"] in existing_ids:
                self.local_index = [d for d in self.local_index if d["id"] != doc["id"]]
            self.local_index.append(doc)
        self._save_local_index()

        # If live Azure credentials exist, push to remote search service
        if not self.mock_mode and settings.AZURE_SEARCH_API_KEY:
            try:
                from azure.core.credentials import AzureKeyCredential
                from azure.search.documents import SearchClient
                credential = AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
                client = SearchClient(
                    endpoint=settings.AZURE_SEARCH_SERVICE_ENDPOINT,
                    index_name=settings.AZURE_SEARCH_INDEX_NAME,
                    credential=credential
                )
                client.upload_documents(documents=indexed_docs)
            except Exception as e:
                print(f"[RAGIndexer] Remote upload warning: {e}")

        return len(indexed_docs)

    def get_total_indexed(self) -> int:
        """Return count of indexed document chunks."""
        return len(self.local_index)
