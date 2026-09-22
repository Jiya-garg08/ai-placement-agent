import re
import json
from pathlib import Path
from typing import List, Optional
import numpy as np

from config.settings import settings
from schemas.rag_schema import SearchResultItem
from rag.embeddings.azure_embedder import AzureEmbedder
from rag.ingestion.indexer import LOCAL_INDEX_FILE


class HybridRetriever:
    """Performs hybrid vector similarity and BM25 keyword retrieval over indexed placement material."""

    def __init__(self, embedder: Optional[AzureEmbedder] = None, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.embedder = embedder or AzureEmbedder(mock_mode=self.mock_mode)

    def search(
        self,
        query: str,
        top_k: int = 4,
        topic_filter: Optional[str] = None,
        min_relevance_score: float = 0.30
    ) -> List[SearchResultItem]:
        """Execute hybrid search query and return ranked SearchResultItems."""
        if self.mock_mode or not settings.AZURE_SEARCH_API_KEY:
            return self._local_hybrid_search(query, top_k, topic_filter, min_relevance_score)

        try:
            return self._azure_hybrid_search(query, top_k, topic_filter)
        except Exception as e:
            # Fallback to local offline search if Azure connection fails
            return self._local_hybrid_search(query, top_k, topic_filter, min_relevance_score)

    def _local_hybrid_search(
        self,
        query: str,
        top_k: int,
        topic_filter: Optional[str],
        min_score: float
    ) -> List[SearchResultItem]:
        """Perform deterministic offline hybrid vector + keyword matching."""
        if not LOCAL_INDEX_FILE.exists():
            return []

        try:
            with open(LOCAL_INDEX_FILE, "r", encoding="utf-8") as f:
                docs = json.load(f)
        except Exception:
            return []

        if not docs:
            return []

        query_vec = np.array(self.embedder.get_embedding(query))
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec = query_vec / q_norm

        query_words = set(re.findall(r'\w+', query.lower()))
        filter_words = set(re.findall(r'\w+', topic_filter.lower().replace("&", "and"))) if topic_filter else set()
        
        # Expand common computer science acronyms for robust matching
        acronym_expansions = {
            "dsa": {"data", "structures", "algorithms"},
            "dbms": {"database", "management", "systems"},
            "os": {"operating", "systems"},
            "cn": {"computer", "networks"},
            "oop": {"object", "oriented", "programming"},
            "ml": {"machine", "learning"},
            "sql": {"sql", "structured", "query"},
        }
        expanded_filters = set(filter_words)
        for w in filter_words:
            if w in acronym_expansions:
                expanded_filters |= acronym_expansions[w]
        filter_words = expanded_filters

        results = []

        for doc in docs:
            # Apply topic filter if specified
            if filter_words:
                doc_topic = f"{doc.get('topic', '')} {doc.get('title', '')}".lower().replace("&", "and")
                doc_topic_words = set(re.findall(r'\w+', doc_topic))
                # If neither topic acronym nor any keyword matches, skip
                if not (filter_words & doc_topic_words):
                    continue

            # 1. Cosine similarity
            doc_vec = np.array(doc.get("content_vector", []))
            if len(doc_vec) == len(query_vec):
                d_norm = np.linalg.norm(doc_vec)
                cos_sim = float(np.dot(query_vec, doc_vec) / (q_norm * d_norm)) if (q_norm * d_norm) > 0 else 0.0
            else:
                cos_sim = 0.0

            # 2. Keyword overlap score
            doc_text = f"{doc.get('title', '')} {doc.get('section', '')} {doc.get('content', '')}".lower()
            doc_words = set(re.findall(r'\w+', doc_text))
            overlap = len(query_words & doc_words)
            keyword_score = overlap / max(len(query_words), 1)

            # 3. Hybrid blend
            hybrid_score = round(0.50 * cos_sim + 0.50 * keyword_score, 4)

            if hybrid_score >= min_score:
                results.append(SearchResultItem(
                    id=doc["id"],
                    title=doc.get("title", "Reference Guide"),
                    topic=doc.get("topic", "Core Computer Science"),
                    section=doc.get("section", "General"),
                    content=doc.get("content", ""),
                    source_file=doc.get("source_file", "knowledge_base.md"),
                    score=hybrid_score
                ))

        # Sort descending by hybrid score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _azure_hybrid_search(
        self,
        query: str,
        top_k: int,
        topic_filter: Optional[str]
    ) -> List[SearchResultItem]:
        """Execute remote hybrid search against Azure AI Search."""
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient
        from azure.search.documents.models import VectorizedQuery

        query_vec = self.embedder.get_embedding(query)
        vector_query = VectorizedQuery(
            vector=query_vec,
            k_nearest_neighbors=top_k,
            fields="content_vector"
        )

        credential = AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
        client = SearchClient(
            endpoint=settings.AZURE_SEARCH_SERVICE_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX_NAME,
            credential=credential
        )

        filter_expr = f"search.ismatch('{topic_filter}', 'topic')" if topic_filter else None

        search_results = client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=filter_expr,
            top=top_k
        )

        items = []
        for r in search_results:
            items.append(SearchResultItem(
                id=r["id"],
                title=r.get("title", ""),
                topic=r.get("topic", ""),
                section=r.get("section", ""),
                content=r.get("content", ""),
                source_file=r.get("source_file", ""),
                score=float(r.get("@search.score", 1.0))
            ))
        return items
