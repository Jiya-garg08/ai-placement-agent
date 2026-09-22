import re
import io
from pathlib import Path
from typing import Union, BinaryIO, Dict, List, Optional

import pypdf
import docx

from config.constants import ALL_TAXONOMY_SKILLS
from config.security import redact_pii
from schemas.resume_schema import ParsedResumeResponse

SECTION_PATTERNS = {
    "skills": re.compile(r'\b(technical\s+skills|skills|technologies|proficiencies|tools)\b', re.IGNORECASE),
    "education": re.compile(r'\b(education|academic\s+background|academics|qualifications)\b', re.IGNORECASE),
    "experience": re.compile(r'\b(work\s+experience|experience|employment|internships)\b', re.IGNORECASE),
    "projects": re.compile(r'\b(projects|academic\s+projects|key\s+projects)\b', re.IGNORECASE),
    "certifications": re.compile(r'\b(certifications|courses|achievements|awards)\b', re.IGNORECASE),
}


class ResumeService:
    """Service to parse, sanitize, and segment resumes from PDF/DOCX formats."""

    @staticmethod
    def extract_text_from_pdf(source: Union[str, Path, BinaryIO]) -> str:
        """Extract text from a PDF file path or binary stream."""
        reader = pypdf.PdfReader(source)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text).strip()

    @staticmethod
    def extract_text_from_docx(source: Union[str, Path, BinaryIO]) -> str:
        """Extract text from a DOCX file path or binary stream."""
        doc = docx.Document(source)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()

    @classmethod
    def extract_text(cls, source: Union[str, Path, BinaryIO], filename: str) -> str:
        """Auto-detect file extension and extract raw text."""
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(source)
        elif ext in (".docx", ".doc"):
            return cls.extract_text_from_docx(source)
        elif ext == ".txt":
            if isinstance(source, (str, Path)):
                with open(source, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            else:
                return source.read().decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file format: '{ext}'. Supported: .pdf, .docx, .txt")

    @classmethod
    def segment_sections(cls, text: str) -> Dict[str, str]:
        """Heuristically segment resume text into named sections."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        sections: Dict[str, List[str]] = {}
        current_section = "summary"
        sections[current_section] = []

        for line in lines:
            # Check if line looks like a header (short length and matches pattern)
            is_header = False
            if len(line.split()) <= 4:
                for sec_name, pattern in SECTION_PATTERNS.items():
                    if pattern.search(line):
                        current_section = sec_name
                        if current_section not in sections:
                            sections[current_section] = []
                        is_header = True
                        break
            if not is_header:
                sections[current_section].append(line)

        return {k: "\n".join(v) for k, v in sections.items() if v}

    @classmethod
    def extract_skills_heuristic(cls, text: str, sections: Optional[Dict[str, str]] = None) -> List[str]:
        """Extract domain and cross-functional skills deterministically using taxonomy and section parsing."""
        detected = set()
        lower_text = text.lower()

        # 1. Match from multi-domain taxonomy
        for skill in ALL_TAXONOMY_SKILLS:
            escaped_skill = re.escape(skill)
            if re.search(rf'\b{escaped_skill}\b', lower_text):
                detected.add(skill.title())

        # 2. Extract dynamic domain skills from the skills section if available
        if sections and "skills" in sections:
            skills_raw = sections["skills"]
            # Split by newlines, commas, semicolons, bullets, and pipes
            tokens = re.split(r'[\n,;•|\-*]', skills_raw)
            for raw_tok in tokens:
                tok = raw_tok.strip()
                # Remove prefixes like "Languages:", "Tools:", etc.
                if ":" in tok:
                    tok = tok.split(":")[-1].strip()
                # Filter valid skill phrases (1-4 words, reasonable length, not pure numbers or URLs)
                words = tok.split()
                if 1 <= len(words) <= 4 and 2 <= len(tok) <= 35:
                    if not any(stop in tok.lower() for stop in ["http", "www", "email", "phone", "profile", "summary"]):
                        detected.add(tok.title())

        return sorted(list(detected))

    @classmethod
    def parse_resume(cls, source: Union[str, Path, BinaryIO], filename: str) -> ParsedResumeResponse:
        """Complete pipeline: extract text, redact PII, segment sections, and extract heuristic skills."""
        raw_text = cls.extract_text(source, filename)
        redacted = redact_pii(raw_text)
        sections = cls.segment_sections(redacted)
        skills = cls.extract_skills_heuristic(redacted, sections)

        return ParsedResumeResponse(
            raw_text=raw_text,
            redacted_text=redacted,
            sections=sections,
            detected_skills=skills
        )
