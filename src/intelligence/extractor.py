from pydoc import text
import re
from typing import Dict, List

# Fixed keyword list (small, explainable, judge-friendly)
SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "account blocked",
    "suspended",
    "limited time",
    "act now",
    "immediately"
]

def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """
    Extracts scam-related intelligence from scammer text.
    Deterministic, rule-based, multi-turn safe.
    """

    phishing_links = re.findall(
        r"https?://[^\s]+",
        text,
        flags=re.IGNORECASE
    )

    phone_numbers = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    upi_ids = re.findall(
        r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b",
        text
    )

    # Loose on purpose (false positives acceptable)
    bank_accounts = re.findall(
        r"\b\d{9,18}\b",
        text
    )

    suspicious_keywords_found = [
        kw for kw in SUSPICIOUS_KEYWORDS
        if kw.lower() in text.lower()
    ]

    return {
        "bankAccounts": list(set(bank_accounts)),
        "upiIds": list(set(upi_ids)),
        "phishingLinks": list(set(phishing_links)),
        "phoneNumbers": list(set(phone_numbers)),
        "suspiciousKeywords": list(set(suspicious_keywords_found))
    }
