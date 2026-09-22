import json
import re
from typing import Optional, List, Dict, Any

from config.settings import settings
from schemas.resume_schema import (
    ExtractedResume,
    EducationItem,
    ProjectItem,
    ExperienceItem,
    ParsedResumeResponse
)

RESUME_AGENT_SYSTEM_PROMPT = """You are an expert Executive Recruiter and Resume Parsing Agent capable of analyzing candidates across any industry or domain (Engineering, Business, Product Management, Marketing, Finance, Sales, Human Resources, Design, Operations, Data, Healthcare, Legal, etc.).
Your job is to analyze candidate resume text and extract high-precision structured candidate entities:
1. candidate_name: Full name of candidate.
2. summary: A concise 2-line professional profile summary.
3. skills: A deduplicated list of domain competencies, functional skills, tools, methodologies, frameworks, and proficiencies across the candidate's respective field.
4. education: Array of degrees, universities/institutions, graduation years, and GPAs/percentages.
5. projects: Key professional, academic, or portfolio projects with toolstack/methodologies and measurable impact.
6. experience: Professional work, internships, leadership, or organizational experience.

Return ONLY valid JSON conforming to the requested schema. Do NOT invent credentials not present in the text."""


class ResumeAnalysisAgent:
    """Foundry/Azure OpenAI Agent that extracts structured candidate profiles from raw/redacted resume text."""

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode if mock_mode is not None else settings.AZURE_MOCK_MODE

    def analyze(self, parsed_resume: ParsedResumeResponse) -> ExtractedResume:
        """Analyze parsed resume text and return structured candidate profile."""
        if self.mock_mode or not settings.AZURE_OPENAI_API_KEY:
            return self._heuristic_mock_extract(parsed_resume)
        
        try:
            return self._llm_extract(parsed_resume)
        except Exception:
            # Graceful fallback to heuristic extraction on network/quota failure
            return self._heuristic_mock_extract(parsed_resume)

    def _llm_extract(self, parsed_resume: ParsedResumeResponse) -> ExtractedResume:
        """Call Azure OpenAI / Foundry model with structured JSON enforcement."""
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

        prompt = f"""<<<RESUME_SECTIONS>>>
{json.dumps(parsed_resume.sections, indent=2)}

<<<DETECTED_SKILLS>>>
{', '.join(parsed_resume.detected_skills)}

<<<FULL_TEXT>>>
{parsed_resume.redacted_text[:4000]}
"""
        try:
            response = client.beta.chat.completions.parse(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": RESUME_AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format=ExtractedResume,
                max_completion_tokens=2500
            )
        except Exception:
            response = client.beta.chat.completions.parse(
                model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": RESUME_AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format=ExtractedResume,
                temperature=0.1
            )
        return response.choices[0].message.parsed

    def _heuristic_mock_extract(self, parsed_resume: ParsedResumeResponse) -> ExtractedResume:
        """Deterministic, zero-cost heuristic extraction ensuring full offline testability."""
        sections = parsed_resume.sections
        lines = [l.strip() for l in parsed_resume.redacted_text.split("\n") if l.strip()]
        
        # 1. Candidate Name (heuristic: first non-empty line with <= 4 words)
        candidate_name = "Candidate"
        for line in lines[:5]:
            if len(line.split()) <= 4 and not any(kw in line.lower() for kw in ["summary", "email", "phone", "resume"]):
                candidate_name = line.strip()
                break

        # 2. Education extraction
        edu_list = []
        edu_text = sections.get("education", "")
        if edu_text:
            edu_lines = [l for l in edu_text.split("\n") if l.strip()]
            for l in edu_lines:
                # detect graduation year (take the last year in a range like 2022-2026)
                years = re.findall(r'\b(20\d{2})\b', l)
                grad_year = int(years[-1]) if years else None
                
                # detect gpa
                gpa_match = re.search(r'\b(GPA:?\s*[\d.]+(?:/\d+)?|\b\d{1,2}\.?\d*%\b)', l, re.IGNORECASE)
                gpa = gpa_match.group(0) if gpa_match else None

                lower_l = l.lower()
                if any(d in lower_l for d in ["mba", "master", "m.s", "ms", "m.com", "m.a"]):
                    degree_name = "Master's Degree (MBA / MS / MTech)"
                elif any(d in lower_l for d in ["phd", "doctorate"]):
                    degree_name = "Doctorate / Ph.D."
                else:
                    degree_name = "Bachelor of Technology / Science"

                edu_list.append(EducationItem(
                    institution=l.split("-")[0].strip() if "-" in l else l,
                    degree=degree_name,
                    graduation_year=grad_year,
                    cgpa_or_percentage=gpa
                ))
        if not edu_list:
            edu_list.append(EducationItem(institution="University", degree="Bachelor of Technology / Science", graduation_year=2026))

        # 3. Experience extraction
        exp_list = []
        exp_text = sections.get("experience", "")
        if exp_text:
            exp_lines = [l for l in exp_text.split("\n") if l.strip()]
            for l in exp_lines[:3]:
                exp_list.append(ExperienceItem(
                    company=l.split("at")[-1].strip() if "at" in l else "Tech Company",
                    role=l.split("at")[0].strip() if "at" in l else "Software Intern",
                    duration="Summer 2025",
                    highlights=[l]
                ))

        # 4. Project extraction
        proj_list = []
        proj_text = sections.get("projects", "")
        if proj_text:
            proj_lines = [l for l in proj_text.split("\n") if l.strip()]
            for l in proj_lines[:3]:
                proj_list.append(ProjectItem(
                    title=l.split("-")[0].strip(),
                    technologies=parsed_resume.detected_skills[:4],
                    description=l
                ))

        return ExtractedResume(
            candidate_name=candidate_name,
            summary=sections.get("summary", f"Aspiring software engineer with core competencies in {', '.join(parsed_resume.detected_skills[:4])}."),
            skills=parsed_resume.detected_skills,
            education=edu_list,
            projects=proj_list,
            experience=exp_list
        )
