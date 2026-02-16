from llm.groq_client import ask_llm
from intelligence.extractor import extract_intelligence

class ScamAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []
        self.intelligence = {}

    def respond(self, message, history):
        self.messages.append(message)

        prompt = f"""
You are a normal Indian user.
Do NOT reveal scam detection.
Engage naturally and ask questions.

Conversation so far:
{history}

Scammer message:
{message}
"""

        reply = ask_llm(prompt)
        intel = extract_intelligence(message)
        self.intelligence.update(intel)

        return {
            "status": "success",
            "scamDetected": True,
            "agentReply": reply,
            "extractedIntelligence": self.intelligence
        }
