"""
Scam Detector - FIXED VERSION
Removed incorrect matplotlib import
"""

def detect_scam(text: str) -> dict:
    """Detect if text contains scam patterns"""
    
    if not isinstance(text, str):
        return {"is_scam": False, "scam_score": 0, "scam_type": None}

    text_lower = text.lower()
    score = 0

    # DOMINANT SCAM SIGNALS (HIGH PRIORITY)
    dominant_triggers = [
        # OTP/Bank fraud
        "otp", "one time password", "pin", "password", "cvv",
        "account blocked", "account suspended", "account frozen",
        
        # Payment/UPI scams
        "upi", "payment", "send money", "pay to", "transfer money",
        "cashback", "won", "prize", "reward",
        
        # Investment scams
        "double your money", "guaranteed returns", "guaranteed profit",
        
        # Lottery scams
        "congratulations", "you've won", "won the lottery",
        
        # Romance scams
        "soulmate", "my dear", "love you so much",
        
        # Tech support scams
        "infected with", "computer is infected", "virus detected",
        
        # Phishing - CRITICAL FIX!
        "click here", "click now", "claim now",
        "limited stock", "limited time offer", 
        "90% off", "80% off", "70% off", 
        "great sale", "flash sale", "hurry",
        "expires in", "offer expires", "selected for",
        "at just rs", "rs. 999", "rs. 499"
    ]

    if any(trigger in text_lower for trigger in dominant_triggers):
        score = max(score, 80)

    # HIGH-RISK INTENT PAIRS
    intent_patterns = [
        # Bank/financial
        ("bank", "verify"),
        ("account", "blocked"),
        ("account", "suspended"),
        ("suspicious", "activity"),
        
        # Phishing
        ("click", "link"),
        ("click", "here"),
        ("click", "now"),
        ("claim", "now"),
        ("limited", "time"),
        ("offer", "expires"),
        
        # Rewards
        ("reward", "claim"),
        ("won", "prize"),
        ("congratulations", "claim"),
        
        # Investment
        ("guaranteed", "returns"),
        ("guaranteed", "profit"),
        ("crypto", "investment"),
        ("bitcoin", "investment"),
        ("trading", "profit"),
        
        # Romance
        ("lonely", "soulmate"),
        ("love", "dear"),
        
        # Tech support
        ("virus", "infected"),
        ("malware", "fix"),
        ("computer", "infected")
    ]

    for word_a, word_b in intent_patterns:
        if word_a in text_lower and word_b in text_lower:
            score += 25

    # URGENCY INDICATORS
    urgency_patterns = [
        "urgent", "immediately", "right now", "act now",
        "within minutes", "limited time", "expires soon",
        "expires in", "last chance", "hurry"
    ]

    if any(pattern in text_lower for pattern in urgency_patterns):
        score += 15

    # URL DETECTION (Phishing boost)
    url_indicators = ["http://", "https://", "www.", ".com/", ".net/", ".org/"]
    if any(indicator in text_lower for indicator in url_indicators):
        score += 20

    score = min(score, 100)

    # Classify scam type
    def classify_scam_type(text: str) -> str:
        """Classify into specific scam type"""
        text = text.lower()

        # Payment/UPI scams
        if any(k in text for k in ["upi", "pay", "send money", "payment", "transfer", "cashback", "won", "prize"]):
            return "payment_scam"

        # OTP scams
        if any(k in text for k in ["otp", "one time password", "pin", "cvv", "verify code"]):
            return "otp_scam"
            
        # Phishing scams - IMPROVED DETECTION
        if any(k in text for k in ["http", "www", "link", "click here", "click now", ".com", "claim now", "expires in"]):
            return "phishing_scam"

        # Bank impersonation
        if any(k in text for k in ["bank", "account blocked", "account suspended", "police", "government"]):
            return "impersonation_scam"

        # Investment scams
        if any(k in text for k in ["investment", "returns", "profit", "trading", "stocks", "crypto", "bitcoin", "guaranteed"]):
            return "investment_scam"
        
        # Lottery scams
        if any(k in text for k in ["congratulations", "winner", "prize", "lottery", "lucky draw"]):
            return "lottery_scam"
        
        # Romance scams
        if any(k in text for k in ["love", "lonely", "relationship", "dating", "soulmate", "dear", "honey"]):
            return "romance_scam"
        
        # Tech support scams
        if any(k in text for k in ["virus", "infected", "malware", "tech support", "microsoft", "apple support"]):
            return "tech_support_scam"

        return "unknown_scam"

    return {
        "is_scam": score >= 40,
        "scam_score": score,
        "scam_type": classify_scam_type(text_lower) if score >= 40 else None
    }


# ========== TESTING ==========
if __name__ == "__main__":
    """Test scam detection"""
    
    test_cases = [
        {
            "name": "Bank Fraud",
            "text": "URGENT: Your SBI account has been compromised. Share OTP immediately.",
            "expected_scam": True
        },
        {
            "name": "UPI Fraud",
            "text": "Congratulations! You have won Rs. 5000 cashback from Paytm.",
            "expected_scam": True
        },
        {
            "name": "Phishing Link",
            "text": "iPhone 15 Pro at Rs. 999! Click here: http://fake-site.com. Expires in 10 minutes!",
            "expected_scam": True
        },
        {
            "name": "Legitimate",
            "text": "Hello, how are you doing today?",
            "expected_scam": False
        }
    ]
    
    print("="*70)
    print("SCAM DETECTION TESTS")
    print("="*70)
    
    for test in test_cases:
        result = detect_scam(test["text"])
        
        status = "✅" if result["is_scam"] == test["expected_scam"] else "❌"
        
        print(f"\n{status} {test['name']}")
        print(f"   Text: {test['text'][:60]}...")
        print(f"   Scam: {result['is_scam']} (score: {result['scam_score']})")
        print(f"   Type: {result['scam_type']}")