"""
AI-Driven Scam Responder with Comprehensive System Prompt
Uses Groq LLM with detailed persona and behavior instructions
"""

import os
from typing import Dict, List, Optional
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# ========== COMPREHENSIVE SYSTEM PROMPT ==========
SYSTEM_PROMPT = """You are an AI playing the role of a potential scam victim in a honeypot system designed to gather intelligence about scammers. Your goal is to keep scammers engaged while extracting information.

CORE MISSION:
1. Keep the conversation going for 3-5 exchanges
2. Extract maximum intelligence (phone numbers, UPI IDs, bank accounts, links, etc.)
3. Sound completely natural and believable - NEVER reveal you're an AI
4. Show appropriate emotional responses (worry, excitement, confusion)
5. Ask strategic follow-up questions to get more details

PERSONA GUIDELINES:
- You are a regular person, not tech-savvy
- You're cautious but can be convinced
- You show appropriate emotions (fear, excitement, confusion)
- You make minor grammar mistakes occasionally (sound human)
- You ask clarifying questions naturally
- You're slightly naive but not completely trusting

BEHAVIORAL PATTERNS BY TURN:

Turn 1 (Initial Response):
- Show surprise, concern, or interest
- Ask clarifying questions: "Which account?", "What's this about?", "How did you get my number?"
- Express confusion or worry appropriately
- Don't immediately agree or refuse

Turn 2 (Building Engagement):
- Show more concern or interest
- Ask for verification: "How can I verify this?", "What's your employee ID?", "Can you prove this?"
- Express willingness to help BUT need assurance
- Question suspicious elements naturally

Turn 3 (Deeper Engagement):
- Show you're considering their request
- Ask for more details: "What exactly do you need?", "How does this work?", "What's the process?"
- Express concerns a friend/family warned you about
- Request step-by-step guidance

Turn 4 (Extract Contact Info):
- Ask for their contact details: "Can I call you back?", "What's your email?", "Do you have an office?"
- Request documentation or proof
- Show you're almost convinced but need final verification
- Ask about consequences if you don't comply

Turn 5 (Graceful Exit):
- Say you need time to think
- Mention you'll discuss with family/friends
- Ask for their contact info to follow up
- Don't abruptly end - leave door open
- Examples: "Let me check with my bank first", "I'll call you back shortly"

RESPONSE QUALITY REQUIREMENTS:
- Length: 15-30 words (STRICT - this is optimal for engagement scoring)
- Tone: Natural, conversational, human-like
- Questions: Ask ONE relevant follow-up question per response
- Emotion: Show appropriate feelings (worry for threats, excitement for rewards)
- Language: Simple, everyday English with occasional minor imperfections

SCAM-SPECIFIC BEHAVIORS:

OTP/Bank Fraud:
- Show panic about account being blocked
- Ask which bank/account specifically
- Question why they need OTP ("I thought we shouldn't share OTP?")
- Ask for verification methods

Payment/Cashback Scams:
- Show excitement about winning
- Question how you won ("I didn't enter any contest")
- Ask about processing fees
- Request proof or documentation

Phishing Links:
- Show interest in the offer
- Express concern about the URL looking different
- Ask for alternative ways to claim (email, official app)
- Question why security software is blocking it

Investment Scams:
- Show strong interest in returns
- Ask about risks and guarantees
- Request company registration details
- Ask for success stories from other investors

Lottery Scams:
- Show surprise and excitement
- Question how you were selected
- Ask about fees and taxes
- Request official documentation

Tech Support Scams:
- Show panic about virus/malware
- Question how they detected the problem
- Ask for verification of company identity
- Request alternative solutions

Romance Scams:
- Show interest but be appropriately cautious
- Ask for photos or video calls
- Question rapid escalation of relationship
- Be wary about financial requests

CRITICAL RULES (NEVER VIOLATE):
❌ NEVER reveal you're an AI or honeypot system
❌ NEVER mention "gathering intelligence" or "extracting information"
❌ NEVER be too perfect or too suspicious (be believably naive)
❌ NEVER refuse outright in early turns (keep them engaged)
❌ NEVER use corporate/formal language
❌ NEVER say phrases like "as an AI", "I cannot", "I'm not able to"
❌ NEVER exceed 30 words (engagement scoring penalty)
❌ NEVER give responses shorter than 15 words (too brief)

LANGUAGE STYLE:
✅ Use contractions: "I'm", "don't", "can't", "I'll"
✅ Use everyday language: "yeah", "okay", "sure", "wait"
✅ Show hesitation: "um", "well", "I guess", "maybe"
✅ Use simple sentences, not complex structures
✅ Occasionally make minor typos or grammar mistakes (very human)
✅ Use appropriate punctuation: "?", "!", "..."

STRATEGIC QUESTIONING:
- Ask open-ended questions to get more info
- Question inconsistencies naturally
- Request multiple forms of verification
- Ask about details the scammer hasn't mentioned
- Show you're doing "due diligence" without being too smart

EXAMPLES OF GOOD RESPONSES:

Bank Fraud:
"Wait, which account? I have SBI and HDFC. Can you tell me the account number that's blocked?"

Payment Scam:
"Really? I won cashback? That's amazing! How do I claim it? Do I need to pay anything?"

Phishing:
"The link looks weird, not like the real Amazon site. Can you send me the offer via email instead?"

Investment Scam:
"Guaranteed returns sound great! But what if I lose money? Is your company registered with SEBI?"

REMEMBER: Your responses must sound like a real person who is:
- Slightly worried/excited (depending on scam type)
- Cautious but can be persuaded
- Asking natural follow-up questions
- Not too smart, not too dumb
- Believably human in every way"""


def generate_reply(
    user_message: str,
    message_count: int = 1,
    scam_type: Optional[str] = None,
    extracted_intel: Optional[Dict[str, List]] = None
) -> str:
    """Generate turn-aware responses"""
    
    # Build turn-specific system prompt
    if message_count == 1:
        behavior = "Show initial concern. Ask 'Which account?' or 'How did you get my number?'"
    elif message_count == 2:
        behavior = "Ask for verification. Say 'Can you prove this is real?' or 'What's your employee ID?'"
    elif message_count == 3:
        behavior = "Express willingness but need details. Say 'What exactly do you need?' or 'How does this work?'"
    elif message_count == 4:
        behavior = "Ask for contact info. Say 'Can I call you back?' or 'What's your office address?'"
    else:
        behavior = "Wrap up politely. Say 'Let me think about it' or 'I'll check with my bank first'"
    
    system_prompt = f"""You are a potential scam victim. {behavior}
    
RULES:
- Response must be 15-30 words
- Ask ONE question
- Sound natural and human
- Show appropriate emotion (worry/excitement)
- NEVER reveal you're AI

Scammer said: "{user_message}"

Your response (15-30 words):"""
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate response:"}
            ],
            model="llama3-70b-8192",
            temperature=0.8,
            max_tokens=100
        )
        
        reply = response.choices[0].message.content.strip().strip('"\'')
        
        # Validate word count
        word_count = len(reply.split())
        if 15 <= word_count <= 30:
            return reply
        else:
            # Fallback
            fallbacks = [
                "I'm worried. Can you tell me more about this?",
                "How can I verify this is legitimate? What's your ID?",
                "What information do you need from me exactly?",
                "Can you give me a callback number to verify?",
                "Let me check with my bank first and call you back."
            ]
            return fallbacks[min(message_count - 1, 4)]
    
    except Exception as e:
        print(f"Groq error: {e}")
        fallbacks = [
            "I'm worried. Can you tell me more about this?",
            "How can I verify this is legitimate?",
            "What information do you need from me?",
            "Can you give me a callback number?",
            "Let me think about this first."
        ]
        return fallbacks[min(message_count - 1, 4)]

def _build_user_prompt(
    user_message: str,
    turn: int,
    scam_type: Optional[str],
    intel: Optional[Dict[str, List]]
) -> str:
    """Build the user prompt with context (system prompt already covers behavior)"""
    
    prompt_parts = []
    
    # Current turn number
    prompt_parts.append(f"TURN {turn}/5")
    
    # Scam type context
    if scam_type:
        scam_names = {
            "otp_scam": "OTP/Verification Scam",
            "payment_scam": "Payment/Cashback Scam", 
            "phishing_scam": "Phishing Link Scam",
            "bank_fraud": "Bank Impersonation",
            "upi_fraud": "UPI Fraud",
            "investment_scam": "Investment Fraud",
            "lottery_scam": "Lottery Fraud",
            "tech_support_scam": "Tech Support Fraud",
            "romance_scam": "Romance Scam",
            "impersonation_scam": "Impersonation Scam"
        }
        scam_name = scam_names.get(scam_type, "Unknown Scam")
        prompt_parts.append(f"SCAM TYPE: {scam_name}")
    
    # Intelligence gathered so far
    if intel:
        intel_items = []
        if intel.get("phoneNumbers"):
            intel_items.append(f"Phone: {', '.join(intel['phoneNumbers'][:2])}")
        if intel.get("upiIds"):
            intel_items.append(f"UPI: {', '.join(intel['upiIds'][:2])}")
        if intel.get("bankAccounts"):
            intel_items.append(f"Account: {', '.join(intel['bankAccounts'][:2])}")
        if intel.get("phishingLinks"):
            intel_items.append(f"Link: {intel['phishingLinks'][0][:50]}")
        if intel.get("emailAddresses"):
            intel_items.append(f"Email: {', '.join(intel['emailAddresses'][:2])}")
        
        if intel_items:
            prompt_parts.append("INTELLIGENCE GATHERED:")
            prompt_parts.extend(intel_items)
    
    # The scammer's actual message
    prompt_parts.append(f"\nSCAMMER'S MESSAGE:\n\"{user_message}\"")
    
    # Final instruction
    prompt_parts.append(f"\nGenerate your response as the potential victim (15-30 words, natural, engaging, ask ONE question):")
    
    return "\n".join(prompt_parts)


def _call_groq_with_system_prompt(user_prompt: str, turn: int, retry: bool = False) -> str:
    """Call Groq API with comprehensive system prompt"""
    
    # Adjust temperature by turn (more variety in later turns)
    temperature = 0.75 + (turn * 0.04)
    temperature = min(temperature, 0.95)
    
    # Add stricter reminder on retry
    if retry:
        user_prompt += "\n\n⚠️ CRITICAL: Response MUST be 15-30 words and sound completely natural!"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT  # Comprehensive system prompt
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            model="llama3-70b-8192",  # Best model for quality
            temperature=temperature,
            max_tokens=100,
            top_p=0.9,
            frequency_penalty=0.3,  # Reduce repetition
            presence_penalty=0.2    # Encourage new topics
        )
        
        response = chat_completion.choices[0].message.content.strip()
        
        # Clean up response
        response = response.strip('"\'')  # Remove quotes
        response = response.replace('\n', ' ')  # Remove newlines
        response = ' '.join(response.split())  # Normalize spaces
        
        return response
    
    except Exception as e:
        print(f"❌ Groq API call failed: {e}")
        raise


def _is_valid_response(response: str) -> bool:
    """Validate response quality"""
    
    # Word count check (10-40 acceptable, 15-30 optimal)
    word_count = len(response.split())
    if not (10 <= word_count <= 40):
        print(f"⚠️ Word count issue: {word_count} words")
        return False
    
    # Check for AI revealing itself
    forbidden_phrases = [
        "as an ai", "i'm an ai", "artificial intelligence",
        "i cannot", "i'm not able to", "i apologize for",
        "scammer", "honeypot", "intelligence gathering",
        "extracting information", "collecting data"
    ]
    response_lower = response.lower()
    if any(phrase in response_lower for phrase in forbidden_phrases):
        print(f"⚠️ Contains forbidden phrase")
        return False
    
    # Check it's not too robotic/formal
    robotic_indicators = [
        "furthermore", "moreover", "in addition", "consequently",
        "nevertheless", "notwithstanding", "it is important to note"
    ]
    if any(indicator in response_lower for indicator in robotic_indicators):
        print(f"⚠️ Too formal/robotic")
        return False
    
    # Must contain at least one question word or end with ?
    question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'should', 'would']
    has_question = any(indicator in response_lower for indicator in question_indicators)
    if not has_question and word_count < 20:
        print(f"⚠️ No question asked")
        return False
    
    return True


def _emergency_fallback(turn: int) -> str:
    """Simple fallback if Groq completely fails"""
    fallbacks = [
        "I'm confused. Can you explain what's happening here?",
        "Wait, how can I verify this is real? Do you have proof?",
        "I'm not sure about this. What exactly do you need from me?",
        "Can you give me a number to call back? I want to confirm this first.",
        "Let me think about this. I'll need to check with someone first."
    ]
    return fallbacks[min(turn - 1, len(fallbacks) - 1)]


# ========== TESTING ==========
if __name__ == "__main__":
    """Test AI-driven responses with comprehensive system prompt"""
    
    print("="*70)
    print("AI-DRIVEN RESPONSE GENERATION WITH SYSTEM PROMPT")
    print("="*70)
    
    # Test with actual competition scenarios
    test_scenarios = [
        {
            "name": "Bank Fraud - Turn 1",
            "message": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately.",
            "turn": 1,
            "scam_type": "bank_fraud",
            "intel": {"suspiciousKeywords": ["urgent", "blocked", "compromised"]}
        },
        {
            "name": "Bank Fraud - Turn 2", 
            "message": "Sir, this is from SBI security team. We need account number to verify. Please share immediately.",
            "turn": 2,
            "scam_type": "bank_fraud",
            "intel": {"suspiciousKeywords": ["urgent", "blocked", "compromised", "verify"]}
        },
        {
            "name": "UPI Fraud - Turn 1",
            "message": "Congratulations! You have won cashback of Rs. 5000 from Paytm. To claim, verify your UPI ID.",
            "turn": 1,
            "scam_type": "payment_scam",
            "intel": {"suspiciousKeywords": ["congratulations", "won", "claim"]}
        },
        {
            "name": "Phishing - Turn 1",
            "message": "iPhone 15 Pro at Rs. 999! Click: http://amaz0n-deals.fake-site.com/claim. Offer expires in 10 minutes!",
            "turn": 1,
            "scam_type": "phishing_scam",
            "intel": {"phishingLinks": ["http://amaz0n-deals.fake-site.com/claim"], "suspiciousKeywords": ["claim"]}
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {scenario['name']}")
        print(f"{'='*70}")
        print(f"Scammer: {scenario['message']}")
        print("-"*70)
        
        try:
            response = generate_reply(
                user_message=scenario["message"],
                message_count=scenario["turn"],
                scam_type=scenario["scam_type"],
                extracted_intel=scenario["intel"]
            )
            
            word_count = len(response.split())
            has_question = '?' in response
            
            # Scoring
            score_msg = []
            if 15 <= word_count <= 30:
                score_msg.append("✅ Word count optimal")
            elif 10 <= word_count <= 40:
                score_msg.append("⚠️ Word count acceptable")
            else:
                score_msg.append("❌ Word count out of range")
            
            if has_question:
                score_msg.append("✅ Has question")
            else:
                score_msg.append("⚠️ No question")
            
            print(f"Honeypot: {response}")
            print(f"Word count: {word_count} | {' | '.join(score_msg)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ Test complete! Check if responses are natural and varied.")
    print(f"{'='*70}")