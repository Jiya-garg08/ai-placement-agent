from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescriptionRequest(BaseModel):
    raw_text: str = Field(..., min_length=20, description="Raw text of the job description")
    company_name: Optional[str] = Field(default=None, max_length=150)
    role_title: Optional[str] = Field(default=None, max_length=150)


class ParsedJobDescription(BaseModel):
    company_name: Optional[str] = None
    role_title: str = Field(default="Software Development Engineer")
    experience_level: str = Field(default="Entry-Level / Fresher (0-1 yrs)")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    domain_keywords: List[str] = Field(default_factory=list)
    raw_text: str
