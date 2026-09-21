import re

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
URL_REGEX = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)')


def redact_pii(text: str) -> str:
    """Mask sensitive PII such as emails and phone numbers before downstream LLM ingestion."""
    if not text:
        return ""
    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
    sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)
    return sanitized


def sanitize_prompt_input(text: str) -> str:
    """Sanitize user-provided text against common prompt-injection attempts and system overrides."""
    if not text:
        return ""
    # Strip null bytes and normalize whitespace
    cleaned = text.replace("\x00", "").strip()
    
    # Neutralize common prompt-override directives
    dangerous_patterns = [
        re.compile(r'ignore\s+(all\s+)?(previous|prior)\s+instructions', re.IGNORECASE),
        re.compile(r'disregard\s+(all\s+)?(previous|prior)\s+instructions', re.IGNORECASE),
        re.compile(r'system\s*:\s*you\s+are\s+now', re.IGNORECASE),
        re.compile(r'you\s+are\s+no\s+longer', re.IGNORECASE),
    ]
    for pattern in dangerous_patterns:
        cleaned = pattern.sub("[SAFETY_FLAGGED_CONTENT_REMOVED]", cleaned)
        
    return cleaned
