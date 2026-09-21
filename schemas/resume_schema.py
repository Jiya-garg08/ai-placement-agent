from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa_or_percentage: Optional[str] = None


class ProjectItem(BaseModel):
    title: str
    technologies: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)


class ExtractedResume(BaseModel):
    candidate_name: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)


class ParsedResumeResponse(BaseModel):
    raw_text: str
    redacted_text: str
    sections: Dict[str, str] = Field(default_factory=dict)
    detected_skills: List[str] = Field(default_factory=list)
