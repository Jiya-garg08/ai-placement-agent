from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeChunk(BaseModel):
    """Normalized educational document chunk prepared for vector indexing and hybrid retrieval."""
    id: str
    title: str
    topic: str
    subtopic: Optional[str] = None
    section: str
    content: str
    token_count: int
    source_file: str

    model_config = ConfigDict(from_attributes=True)


class CitationSource(BaseModel):
    """Source reference citation verifying groundedness in educational material."""
    title: str
    section: str
    source_file: str
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    """Individual retrieval hit from hybrid search."""
    id: str
    title: str
    topic: str
    section: str
    content: str
    source_file: str
    score: float


class TutorQueryRequest(BaseModel):
    student_id: int
    query: str
    topic_context: Optional[str] = None
    chat_history: List[Dict[str, str]] = Field(default_factory=list)


class TutorResponse(BaseModel):
    query: str
    answer: str
    citations: List[CitationSource] = Field(default_factory=list)
    grounded: bool = True
