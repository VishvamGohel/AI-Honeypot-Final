# src/memory/session_store.py

def create_new_session():
    return {
        "messages": [],
        "turns": 0,
        "scam_score": 0,
        "is_scam": False,
        "scam_type": None,  # FIX: Initialize scam_type
        "callback_sent": False,
        "intelligence": {
            "bankAccounts": set(),
            "upiIds": set(),
            "phishingLinks": set(),
            "phoneNumbers": set(),
            "suspiciousKeywords": set()
        },
        "completed": False
    }


sessions = {}