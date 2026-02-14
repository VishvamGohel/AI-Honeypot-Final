def detect_scam(text: str) -> dict:
    if not isinstance(text, str):
        return {"is_scam": False, "scam_score": 0}

    text = text.lower()
    score = 0

    # DOMINANT SCAM SIGNALS (OVERRIDE)
    dominant_triggers = [
        "otp", "one time password", "pin", "password", "cvv",
        "install app", "apk",
        "upi", "pay to", "send money",
        "account blocked", "account suspended", "account frozen"
    ]

    if any(trigger in text for trigger in dominant_triggers):
        score = max(score, 80)

    # HIGH-RISK INTENT PAIRS
    intent_patterns = [
        ("bank", "verify"),
        ("suspicious", "activity"),
        ("click", "link"),
        ("reward", "claim"),
        ("guaranteed", "returns"),
        ("crypto", "investment")
    ]

    for a, b in intent_patterns:
        if a in text and b in text:
            score += 25

    # PRESSURE / URGENCY
    urgency_words = ["urgent", "immediately", "now", "within minutes"]

    if any(word in text for word in urgency_words):
        score += 15

    score = min(score, 100)

    def classify_scam_type(text: str) -> str:
        text = text.lower()

        if any(k in text for k in ["upi", "pay", "send money", "payment"]):
            return "payment_scam"

        if any(k in text for k in ["otp", "one time password", "pin", "cvv"]):
            return "otp_scam"
        if any(k in text for k in ["http", "www", "link", "click"]):
            return "phishing_scam"

        if any(k in text for k in ["bank", "account blocked", "account suspended"]):
            return "impersonation_scam"

        return "unknown_scam"


    return {
        "is_scam": score >= 40,
        "scam_score": score,
        "scam_type": classify_scam_type(text) if score >= 40 else None
    }
