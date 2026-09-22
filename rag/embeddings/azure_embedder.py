import os
import json
import hashlib
from pathlib import Path
from typing import List, Optional
import numpy as np

from config.settings import settings

EMBEDDING_DIM = 1536
CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "embedding_cache.json"


class AzureEmbedder:
    """Generates 1536-dimensional vector embeddings with local disk caching and offline mock support."""

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load persistent disk cache of computed embeddings."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def _hash_text(self, text: str) -> str:
        """Compute SHA256 hash for cache key."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic 1536-dim unit vector from text hash."""
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(EMBEDDING_DIM)
        # Normalize to unit vector for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def get_embedding(self, text: str) -> List[float]:
        """Generate or retrieve cached embedding for a single text chunk."""
        h = self._hash_text(text)
        if h in self.cache:
            return self.cache[h]

        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            vec = self._generate_mock_embedding(text)
            self.cache[h] = vec
            self._save_cache()
            return vec

        # Live Azure OpenAI call
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            resp = client.embeddings.create(
                model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                input=text
            )
            vec = resp.data[0].embedding
            self.cache[h] = vec
            self._save_cache()
            return vec
        except Exception:
            # Fallback to mock on API error to prevent crashing
            vec = self._generate_mock_embedding(text)
            self.cache[h] = vec
            self._save_cache()
            return vec

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of texts."""
        return [self.get_embedding(t) for t in texts]
