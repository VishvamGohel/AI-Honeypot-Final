# src/memory/session_store.py

import time

def create_new_session():
    return {
        "messages": [],
        "turns": 0,
        "scam_score": 0,
        "is_scam": False,
        "scam_type": None,
        "callback_sent": False,
        "start_time": time.time(),  # CRITICAL: Track session start for engagement duration
        "intelligence": {
            # ORIGINAL 5 TYPES
            "bankAccounts": set(),
            "upiIds": set(),
            "phishingLinks": set(),
            "phoneNumbers": set(),
            "suspiciousKeywords": set(),
            
            # NEW 4 TYPES
            "emailAddresses": set(),
            "cryptoWallets": set(),
            "socialHandles": set(),
            "ipAddresses": set()
        },
        "completed": False
    }


sessions = {}