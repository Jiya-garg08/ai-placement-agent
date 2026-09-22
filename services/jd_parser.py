import re
from typing import List, Dict, Tuple, Optional
from config.constants import ALL_TAXONOMY_SKILLS, STANDARD_SKILL_TAXONOMY
from schemas.jd_schema import ParsedJobDescription

ROLE_PATTERNS = [
    # Engineering & Tech
    (re.compile(r'\b(software\s+(development\s+)?engineer(\s+[1i]+)?|sde[- ]?[1i]?)\b', re.IGNORECASE), "Software Development Engineer (SDE)"),
    (re.compile(r'\b(backend\s+engineer|backend\s+developer)\b', re.IGNORECASE), "Backend Engineer"),
    (re.compile(r'\b(frontend\s+engineer|frontend\s+developer|ui\s+engineer)\b', re.IGNORECASE), "Frontend Engineer"),
    (re.compile(r'\b(full\s*stack\s+(engineer|developer))\b', re.IGNORECASE), "Full Stack Engineer"),
    (re.compile(r'\b(data\s+engineer)\b', re.IGNORECASE), "Data Engineer"),
    (re.compile(r'\b(machine\s+learning\s+engineer|ml\s+engineer|ai\s+engineer)\b', re.IGNORECASE), "Machine Learning Engineer"),
    (re.compile(r'\b(devops\s+engineer|cloud\s+engineer|sre)\b', re.IGNORECASE), "DevOps / Cloud Engineer"),
    (re.compile(r'\b(data\s+scientist)\b', re.IGNORECASE), "Data Scientist"),

    # Product & Project Management
    (re.compile(r'\b(product\s+manager|associate\s+product\s+manager|apm|tpm)\b', re.IGNORECASE), "Product Manager"),
    (re.compile(r'\b(project\s+manager|scrum\s+master|program\s+manager)\b', re.IGNORECASE), "Project / Program Manager"),

    # Data & Business Analysis
    (re.compile(r'\b(business\s+analyst|bi\s+analyst|data\s+analyst)\b', re.IGNORECASE), "Data & Business Analyst"),

    # Marketing & Growth
    (re.compile(r'\b(digital\s+marketing|marketing\s+manager|growth\s+lead|growth\s+marketer|seo\s+specialist|content\s+strategist)\b', re.IGNORECASE), "Marketing & Growth Specialist"),

    # Finance, Accounting & Banking
    (re.compile(r'\b(financial\s+analyst|investment\s+banking|accountant|auditor|finance\s+manager)\b', re.IGNORECASE), "Financial Analyst"),

    # Human Resources & People
    (re.compile(r'\b(human\s+resources|hr\s+manager|talent\s+acquisition|recruiter|hr\s+specialist)\b', re.IGNORECASE), "Human Resources / Talent Specialist"),

    # UI/UX & Design
    (re.compile(r'\b(ui/ux\s+designer|product\s+designer|ux\s+researcher|visual\s+designer|graphic\s+designer)\b', re.IGNORECASE), "UI/UX & Product Designer"),

    # Sales, Account & Operations
    (re.compile(r'\b(account\s+executive|sales\s+manager|business\s+development|bdr|sdr)\b', re.IGNORECASE), "Sales & Business Development"),
    (re.compile(r'\b(operations\s+manager|supply\s+chain\s+analyst|logistics\s+manager)\b', re.IGNORECASE), "Operations & Supply Chain Manager"),
    (re.compile(r'\b(management\s+consultant|strategy\s+consultant)\b', re.IGNORECASE), "Management Consultant")
]

EXPERIENCE_PATTERNS = [
    (re.compile(r'\b(fresher|new\s+grad(uate)?|campus|entry[- ]level|0[- ]1\s*years?)\b', re.IGNORECASE), "Entry-Level / Fresher (0-1 yrs)"),
    (re.compile(r'\b(1[- ]3\s*years?|junior)\b', re.IGNORECASE), "Junior (1-3 yrs)"),
    (re.compile(r'\b(3[- ]5\s*years?|mid[- ]level)\b', re.IGNORECASE), "Mid-Level (3-5 yrs)"),
    (re.compile(r'\b(5\+?\s*years?|senior|lead)\b', re.IGNORECASE), "Senior / Lead (5+ yrs)")
]

DOMAIN_KEYWORDS_POOL = [
    # Technical & Engineering
    "Scalability", "Microservices", "RESTful APIs", "Distributed Systems",
    "CI/CD", "Agile", "Scrum", "High Availability", "System Architecture",
    "Unit Testing", "Test-Driven Development", "Containerization", "Code Quality",
    # Business, Strategy, Product & Operations
    "Stakeholder Management", "KPI Tracking", "A/B Testing", "Cross-Functional",
    "Financial Modeling", "Market Analysis", "Process Optimization", "Customer Retention",
    "User Research", "Go-To-Market", "Budgeting", "Product Strategy", "Lead Generation"
]


class JobDescriptionParser:
    """Deterministic parser for Job Descriptions to extract roles, experience, skills, and keywords across all fields."""

    @staticmethod
    def detect_role(text: str, fallback: Optional[str] = None) -> str:
        """Detect the target role from JD title or description text across any domain."""
        for pattern, role in ROLE_PATTERNS:
            if pattern.search(text):
                return role

        # Heuristic check for "Position:", "Role:", "Title:" in top lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for l in lines[:5]:
            match = re.search(r'\b(position|role|job\s+title)\s*:\s*([A-Za-z0-9\s/()-]+)', l, re.IGNORECASE)
            if match:
                extracted = match.group(2).strip()
                if 2 <= len(extracted) <= 50:
                    return extracted.title()

        return fallback or "Professional Role"

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
