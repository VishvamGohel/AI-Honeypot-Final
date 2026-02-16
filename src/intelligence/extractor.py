"""
Enhanced Intelligence Extractor - Competition Optimized
Target: 30-35/40 points (up from 0-10)

Key improvements:
1. Better regex patterns for phone, bank, UPI
2. Conversation history extraction
3. 50+ suspicious keywords (was 20)
4. Proper validation to reduce false positives
"""

import re
from typing import Dict, List, Set

# EXPANDED: 50+ suspicious keywords (was ~20)
SUSPICIOUS_KEYWORDS = [
    # Urgency (15 keywords)
    "urgent", "immediately", "now", "asap", "hurry", "quick", "fast",
    "expire", "expiring", "expires", "last chance", "limited time",
    "act now", "don't wait", "time sensitive",
    
    # Threats (12 keywords)
    "blocked", "block", "suspend", "suspended", "lock", "locked",
    "freeze", "frozen", "deactivate", "terminate", "cancel", "delete",
    
    # Financial (18 keywords)
    "verify", "verification", "confirm", "update", "validate", "activate",
    "otp", "cvv", "pin", "password", "account", "bank", "card",
    "payment", "transaction", "refund", "cashback", "transfer",
    
    # Rewards (12 keywords)
    "won", "winner", "prize", "reward", "congratulations", "lottery",
    "jackpot", "claim", "free", "bonus", "offer", "promotion",
    
    # Investment (10 keywords)
    "guaranteed", "profit", "returns", "investment", "crypto",
    "bitcoin", "trading", "forex", "stocks", "double",
    
    # Tech Support (6 keywords)
    "virus", "malware", "infected", "hacked", "breach", "compromised",
    
    # Actions (12 keywords)
    "click", "call", "send", "share", "provide", "download",
    "install", "open", "visit", "login", "register", "submit",
    
    # Impersonation (8 keywords)
    "sbi", "hdfc", "icici", "axis", "amazon", "government", "police", "official",
    
    # Security (5 keywords)
    "security", "unauthorized", "suspicious", "activity", "fraud"
]


def extract_intelligence(text: str, conversation_history: List[Dict] = None) -> Dict[str, List[str]]:
    """
    Extract ALL 9 intelligence types from text and conversation history.
    
    CRITICAL: Now extracts from full conversation, not just current message!
    This is key to scoring high on multi-turn scenarios.
    
    Args:
        text: Current message text
        conversation_history: Previous messages (from session["messages"])
    
    Returns:
        Dictionary with 9 intelligence types
    """
    
    # CRITICAL FIX: Combine current text with conversation history
    full_text = text
    if conversation_history:
        for msg in conversation_history:
            if isinstance(msg, dict) and "text" in msg:
                full_text += " " + msg["text"]
    
    # Initialize result dictionary
    intel = {
        # ORIGINAL 5 TYPES
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": [],
        
        # NEW 4 TYPES
        "emailAddresses": [],
        "cryptoWallets": [],
        "socialHandles": [],
        "ipAddresses": []
    }
    
    # ========== 1. PHONE NUMBERS ==========
    # IMPROVED: Better patterns + validation
    phone_patterns = [
        r'\+91[\s-]?[6-9]\d{9}',      # +91 with Indian mobile
        r'\b91[6-9]\d{9}\b',          # 91 prefix without +
        r'\b[6-9]\d{9}\b',            # 10-digit Indian mobile
    ]
    
    phones = set()
    for pattern in phone_patterns:
        matches = re.findall(pattern, full_text)
        for match in matches:
            # Clean and validate
            clean = re.sub(r'[^\d]', '', match)
            # Validate: 10-12 digits, starts with 6-9 if 10 digits
            if len(clean) == 10 and clean[0] in '6789':
                phones.add(clean)
            elif 11 <= len(clean) <= 12:  # With country code
                phones.add(clean)
    
    intel["phoneNumbers"] = sorted(list(phones))
    
    # ========== 2. UPI IDs ==========
    # IMPROVED: Only match known UPI providers
    upi_providers = ['paytm', 'phonepe', 'googlepay', 'gpay', 'upi', 'ybl', 
                     'okhdfcbank', 'okicici', 'oksbi', 'okaxis', 'ibl', 
                     'airtel', 'freecharge', 'amazonpay']
    
    # Pattern: anything@provider
    upi_pattern = r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\b'
    potential_upis = re.findall(upi_pattern, full_text)
    
    upis = set()
    for match in potential_upis:
        match_lower = match.lower()
        # Check if it contains a known UPI provider
        if any(provider in match_lower for provider in upi_providers):
            upis.add(match)
    
    intel["upiIds"] = sorted(list(upis))
    
    # ========== 3. BANK ACCOUNTS ==========
    # IMPROVED: Context-aware + IFSC codes
    bank_accounts = set()
    
    # Pattern 1: With context (A/C, Account, etc.)
    context_pattern = r'(?:acc(?:ou?nt)?|a/?c|no\.?)\s*:?\s*(\d{9,18})'
    matches = re.findall(context_pattern, full_text, re.IGNORECASE)
    bank_accounts.update(matches)
    
    # Pattern 2: IFSC codes (always 11 chars: XXXX0XXXXXX)
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    matches = re.findall(ifsc_pattern, full_text, re.IGNORECASE)
    bank_accounts.update([m.upper() for m in matches])
    
    # Pattern 3: Standalone long numbers (9-18 digits)
    # BUT: Avoid phone numbers (10 digits starting with 6-9)
    standalone_pattern = r'\b\d{9,18}\b'
    matches = re.findall(standalone_pattern, full_text)
    for match in matches:
        # Exclude 10-digit phone numbers
        if not (len(match) == 10 and match[0] in '6789'):
            # Exclude very long sequences (likely not account numbers)
            if len(match) <= 18:
                bank_accounts.add(match)
    
    intel["bankAccounts"] = sorted(list(bank_accounts))
    
    # ========== 4. PHISHING LINKS ==========
    # IMPROVED: Better URL detection + obfuscated links
    links = set()
    
    # Pattern 1: Standard URLs
    url_pattern = r'https?://[^\s]+'
    matches = re.findall(url_pattern, full_text, re.IGNORECASE)
    links.update(matches)
    
    # Pattern 2: www. links
    www_pattern = r'www\.[^\s]+'
    matches = re.findall(www_pattern, full_text, re.IGNORECASE)
    links.update(matches)
    
    # Pattern 3: domain.com/path format
    domain_pattern = r'\b[a-z0-9.-]+\.(?:com|net|org|in|co|xyz|tk|ml)/[^\s]*'
    matches = re.findall(domain_pattern, full_text, re.IGNORECASE)
    links.update(matches)
    
    intel["phishingLinks"] = sorted(list(links))
    
    # ========== 5. SUSPICIOUS KEYWORDS ==========
    keywords = set()
    text_lower = full_text.lower()
    
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.lower() in text_lower:
            keywords.add(keyword)
    
    intel["suspiciousKeywords"] = sorted(list(keywords))
    
    # ========== 6. EMAIL ADDRESSES (NEW) ==========
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    emails = set(re.findall(email_pattern, full_text))
    
    # Filter out UPI IDs (already captured)
    emails = {e for e in emails if e not in intel["upiIds"]}
    
    intel["emailAddresses"] = sorted(list(emails))
    
    # ========== 7. CRYPTO WALLETS (NEW) ==========
    crypto = set()
    
    # Bitcoin (legacy): starts with 1 or 3, 26-35 chars
    btc_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
    crypto.update(re.findall(btc_pattern, full_text))
    
    # Bitcoin (bech32): starts with bc1, 42-62 chars
    bech32_pattern = r'\bbc1[a-z0-9]{39,59}\b'
    crypto.update(re.findall(bech32_pattern, full_text, re.IGNORECASE))
    
    # Ethereum: 0x followed by 40 hex chars
    eth_pattern = r'\b0x[a-fA-F0-9]{40}\b'
    crypto.update(re.findall(eth_pattern, full_text))
    
    intel["cryptoWallets"] = sorted(list(crypto))
    
    # ========== 8. SOCIAL HANDLES (NEW) ==========
    handles = set()
    
    # @mentions (Twitter/X, Instagram style)
    at_pattern = r'@[a-zA-Z0-9_]{1,30}'
    handles.update(re.findall(at_pattern, full_text))
    
    # Social media URLs
    social_url_pattern = r'(?:instagram|facebook|telegram|twitter|whatsapp)\.com/([a-zA-Z0-9._]+)'
    matches = re.findall(social_url_pattern, full_text, re.IGNORECASE)
    handles.update(matches)
    
    # Telegram: t.me/username
    telegram_pattern = r't\.me/([a-zA-Z0-9_]+)'
    matches = re.findall(telegram_pattern, full_text, re.IGNORECASE)
    handles.update(matches)
    
    intel["socialHandles"] = sorted(list(handles))
    
    # ========== 9. IP ADDRESSES (NEW) ==========
    # IPv4 pattern with validation
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    potential_ips = re.findall(ip_pattern, full_text)
    
    ips = set()
    for ip in potential_ips:
        # Validate each octet is 0-255
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets if octet.isdigit()):
            ips.add(ip)
    
    intel["ipAddresses"] = sorted(list(ips))
    
    return intel


def calculate_extraction_score(intel: Dict[str, List]) -> float:
    """
    Calculate extraction score based on competition criteria.
    Max 40 points distributed as documented in competition_test_02.py
    
    This helps you understand your score during development.
    """
    score = 0.0
    
    score += min(len(intel.get("phoneNumbers", [])) * 5, 10)
    score += min(len(intel.get("upiIds", [])) * 5, 10)
    score += min(len(intel.get("bankAccounts", [])) * 10, 10)
    score += min(len(intel.get("phishingLinks", [])) * 3, 5)
    score += min(len(intel.get("suspiciousKeywords", [])) * 0.5, 5)
    score += min(len(intel.get("emailAddresses", [])) * 3, 5)
    score += min(len(intel.get("cryptoWallets", [])) * 5, 5)
    score += min(len(intel.get("socialHandles", [])) * 2, 5)
    
    return min(score, 40.0)


# ========== TESTING ==========
if __name__ == "__main__":
    # Test with competition scenarios
    test_cases = [
        {
            "name": "Bank Fraud",
            "text": "URGENT: Your SBI account 1234567890 will be blocked. Call 9876543210 immediately.",
            "expected": {
                "phoneNumbers": 1,
                "bankAccounts": 1,
                "keywords": 3  # urgent, blocked, immediately
            }
        },
        {
            "name": "UPI Fraud",
            "text": "Send payment to scammer@paytm to claim ₹50,000 cashback!",
            "expected": {
                "upiIds": 1,
                "keywords": 2  # claim, cashback
            }
        },
        {
            "name": "Phishing",
            "text": "Click here: http://fake-amazon.com/verify or email support@scam.com",
            "expected": {
                "phishingLinks": 1,
                "emailAddresses": 1,
                "keywords": 1  # click
            }
        }
    ]
    
    print("="*70)
    print("INTELLIGENCE EXTRACTION TESTS")
    print("="*70)
    
    for test in test_cases:
        print(f"\n🧪 TEST: {test['name']}")
        print(f"Message: {test['text']}")
        
        intel = extract_intelligence(test['text'])
        score = calculate_extraction_score(intel)
        
        print(f"\n📊 EXTRACTED:")
        for key, values in intel.items():
            if values:
                print(f"  {key}: {values}")
        
        print(f"\n💯 SCORE: {score}/40")
        
        # Validate expectations
        for key, expected_count in test['expected'].items():
            actual = len(intel.get(key, []))
            status = "✅" if actual >= expected_count else "❌"
            print(f"{status} {key}: expected >={expected_count}, got {actual}")