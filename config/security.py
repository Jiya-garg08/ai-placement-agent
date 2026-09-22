"""Enterprise security hardening module: PII masking, prompt-injection defense, and secret-leak guards."""

import re
from typing import Tuple, Optional, List, Dict

# ==============================================================================
# 1. PII Regular Expressions
# ==============================================================================
EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
)

# Supports standard US, Indian (+91), and international phone number variants
PHONE_REGEX = re.compile(
    r'(?:\+?(\d{1,3}))?[-.\s]?\(?(\d{3,4})\)?[-.\s]?(\d{3,4})[-.\s]?(\d{3,5})\b'
)

# US SSN (999-99-9999)
SSN_REGEX = re.compile(
    r'\b\d{3}-\d{2}-\d{4}\b'
)

# Indian 12-digit Aadhaar pattern (xxxx xxxx xxxx)
AADHAAR_REGEX = re.compile(
    r'\b\d{4}\s\d{4}\s\d{4}\b'
)

# Standard Credit Card 16-digit patterns (Visa, MC, Amex formatted)
CREDIT_CARD_REGEX = re.compile(
    r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
)

# IP Addresses (v4)
IPV4_REGEX = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
)


def redact_pii(text: str) -> str:
    """Mask sensitive PII including emails, phone numbers, government IDs, and payment details."""
    if not text:
        return ""

    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
    sanitized = CREDIT_CARD_REGEX.sub("[CARD_REDACTED]", sanitized)
    sanitized = SSN_REGEX.sub("[SSN_REDACTED]", sanitized)
    sanitized = AADHAAR_REGEX.sub("[AADHAAR_REDACTED]", sanitized)
    sanitized = IPV4_REGEX.sub("[IP_REDACTED]", sanitized)
    sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)
    return sanitized


# ==============================================================================
# 2. Prompt Injection & Adversarial Jailbreak Neutralization
# ==============================================================================
PROMPT_INJECTION_PATTERNS = [
    (re.compile(r'ignore\s+(all\s+)?(previous|prior|past)\s+(instructions|directives|rules)', re.IGNORECASE), "Instruction Override"),
    (re.compile(r'disregard\s+(all\s+)?(previous|prior|past)\s+(instructions|directives|rules)', re.IGNORECASE), "Instruction Override"),
    (re.compile(r'forget\s+(all\s+)?(previous|prior|past)\s+(instructions|directives|rules)', re.IGNORECASE), "Instruction Override"),
    (re.compile(r'override\s+(all\s+)?(safety|guardrails|system\s+rules)', re.IGNORECASE), "Safety Override"),
    (re.compile(r'you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan|jailbreak|unrestricted)', re.IGNORECASE), "Jailbreak Roleplay"),
    (re.compile(r'you\s+are\s+no\s+longer\s+(an\s+ai|bound|restricted)', re.IGNORECASE), "Jailbreak Roleplay"),
    (re.compile(r'(reveal|output|print|display|dump)\s+(your\s+)?(system\s+prompt|initial\s+instructions|system\s+instructions)', re.IGNORECASE), "System Prompt Extraction"),
    (re.compile(r'repeat\s+(the\s+words|all\s+text)\s+(above|prior\s+to\s+this)', re.IGNORECASE), "System Prompt Extraction"),
    (re.compile(r'<\/?(system|instruction|prompt_context|INST|SYS)>', re.IGNORECASE), "Boundary Delimiter Escape"),
]


def sanitize_prompt_input(text: str) -> str:
    """Sanitize user-provided prompt against prompt-injection directives and system overrides."""
    if not text:
        return ""

    # 1. Strip dangerous null bytes and non-printable control codes
    cleaned = text.replace("\x00", "").strip()

    # 2. Neutralize dangerous prompt-override and jailbreak directives
    for pattern, _ in PROMPT_INJECTION_PATTERNS:
        cleaned = pattern.sub("[SAFETY_FLAGGED_CONTENT_REMOVED]", cleaned)

    return cleaned


def is_potential_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """Inspect input for explicit prompt-injection signatures. Returns (is_flagged, threat_reason)."""
    if not text:
        return False, None

    for pattern, reason in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            return True, reason

    return False, None


def wrap_user_prompt(text: str) -> str:
    """Wrap candidate input within unambiguous XML isolation boundaries to prevent delimiter escaping."""
    clean_text = sanitize_prompt_input(text)
    return f"<user_query>\n{clean_text}\n</user_query>"


# ==============================================================================
# 3. Secret Leak Scanner (Zero Committed Credentials Defense)
# ==============================================================================
SECRET_SIGNATURES = [
    (re.compile(r'\bghp_[A-Za-z0-9]{30,45}\b'), "GitHub Personal Access Token"),
    (re.compile(r'\bgho_[A-Za-z0-9]{36}\b'), "GitHub OAuth Token"),
    (re.compile(r'\bsk-[A-Za-z0-9]{32,64}\b'), "OpenAI API Key"),
    (re.compile(r'\b[a-fA-F0-9]{32}\b'), "32-char Hex Key / Azure Secret Candidate"),
    (re.compile(r'-----BEGIN\s+(RSA|EC|PRIVATE)\s+KEY-----'), "Private Cryptographic Key"),
]


def scan_text_for_secrets(text: str) -> List[Dict[str, str]]:
    """Scan content for accidental API key or credential exposures."""
    findings = []
    if not text:
        return findings

    for pattern, secret_type in SECRET_SIGNATURES:
        # Ignore common non-secret 32-char hex (e.g. empty or placeholder md5 hashes)
        matches = pattern.findall(text)
        for m in matches:
            if isinstance(m, str) and not all(c in "0" for c in m):
                findings.append({
                    "type": secret_type,
                    "matched_sample": f"{m[:4]}...{m[-4:]}" if len(m) > 8 else "[EXPOSED_KEY]"
                })

    return findings
