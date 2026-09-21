import re
from typing import List, Dict, Tuple, Optional
from config.constants import ALL_TAXONOMY_SKILLS, STANDARD_SKILL_TAXONOMY
from schemas.jd_schema import ParsedJobDescription

ROLE_PATTERNS = [
    (re.compile(r'\b(software\s+(development\s+)?engineer(\s+[1i]+)?|sde[- ]?[1i]?)\b', re.IGNORECASE), "Software Development Engineer (SDE)"),
    (re.compile(r'\b(backend\s+engineer|backend\s+developer)\b', re.IGNORECASE), "Backend Engineer"),
    (re.compile(r'\b(frontend\s+engineer|frontend\s+developer|ui\s+engineer)\b', re.IGNORECASE), "Frontend Engineer"),
    (re.compile(r'\b(full\s*stack\s+(engineer|developer))\b', re.IGNORECASE), "Full Stack Engineer"),
    (re.compile(r'\b(data\s+engineer)\b', re.IGNORECASE), "Data Engineer"),
    (re.compile(r'\b(machine\s+learning\s+engineer|ml\s+engineer|ai\s+engineer)\b', re.IGNORECASE), "Machine Learning Engineer"),
    (re.compile(r'\b(devops\s+engineer|cloud\s+engineer|sre)\b', re.IGNORECASE), "DevOps / Cloud Engineer")
]

EXPERIENCE_PATTERNS = [
    (re.compile(r'\b(fresher|new\s+grad(uate)?|campus|entry[- ]level|0[- ]1\s*years?)\b', re.IGNORECASE), "Entry-Level / Fresher (0-1 yrs)"),
    (re.compile(r'\b(1[- ]3\s*years?|junior)\b', re.IGNORECASE), "Junior (1-3 yrs)"),
    (re.compile(r'\b(3[- ]5\s*years?|mid[- ]level)\b', re.IGNORECASE), "Mid-Level (3-5 yrs)"),
    (re.compile(r'\b(5\+?\s*years?|senior|lead)\b', re.IGNORECASE), "Senior / Lead (5+ yrs)")
]

DOMAIN_KEYWORDS_POOL = [
    "Scalability", "Microservices", "RESTful APIs", "Distributed Systems",
    "CI/CD", "Agile", "Scrum", "High Availability", "System Architecture",
    "Unit Testing", "Test-Driven Development", "Containerization", "Code Quality"
]


class JobDescriptionParser:
    """Deterministic parser for Job Descriptions to extract roles, experience, skills, and keywords."""

    @staticmethod
    def detect_role(text: str, fallback: Optional[str] = None) -> str:
        """Detect the target role from JD title or description text."""
        for pattern, role in ROLE_PATTERNS:
            if pattern.search(text):
                return role
        return fallback or "Software Development Engineer (SDE)"

    @staticmethod
    def detect_experience_level(text: str) -> str:
        """Detect required seniority or experience level."""
        for pattern, level in EXPERIENCE_PATTERNS:
            if pattern.search(text):
                return level
        return "Entry-Level / Fresher (0-1 yrs)"

    @staticmethod
    def extract_skills_and_preferences(text: str) -> Tuple[List[str], List[str]]:
        """Separate skills mentioned in mandatory sections vs preferred/bonus sections."""
        # Split text into sections if headers exist
        required_text = text
        preferred_text = ""

        # Look for split markers
        preferred_split = re.split(r'\b(nice\s+to\s+have|preferred\s+qualifications|good\s+to\s+have|bonus)\b', text, flags=re.IGNORECASE)
        if len(preferred_split) > 2:
            required_text = preferred_split[0]
            preferred_text = "".join(preferred_split[2:])

        required_skills = set()
        preferred_skills = set()

        for skill in ALL_TAXONOMY_SKILLS:
            escaped = re.escape(skill)
            pattern = rf'\b{escaped}\b'
            if re.search(pattern, required_text, re.IGNORECASE):
                required_skills.add(skill.title())
            elif preferred_text and re.search(pattern, preferred_text, re.IGNORECASE):
                preferred_skills.add(skill.title())

        # If a skill is in both, promote it to required
        preferred_skills = preferred_skills - required_skills

        return sorted(list(required_skills)), sorted(list(preferred_skills))

    @staticmethod
    def extract_domain_keywords(text: str) -> List[str]:
        """Extract high-level technical domain keywords from the JD."""
        found = set()
        for kw in DOMAIN_KEYWORDS_POOL:
            if re.search(rf'\b{re.escape(kw)}\b', text, re.IGNORECASE):
                found.add(kw)
        return sorted(list(found))

    @classmethod
    def parse(cls, raw_text: str, company_name: Optional[str] = None, role_title: Optional[str] = None) -> ParsedJobDescription:
        """Execute full parsing pipeline on job description text."""
        detected_role = role_title or cls.detect_role(raw_text)
        detected_exp = cls.detect_experience_level(raw_text)
        required_skills, preferred_skills = cls.extract_skills_and_preferences(raw_text)
        keywords = cls.extract_domain_keywords(raw_text)

        return ParsedJobDescription(
            company_name=company_name,
            role_title=detected_role,
            experience_level=detected_exp,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            domain_keywords=keywords,
            raw_text=raw_text
        )
