# src/api/server.py - IMPROVED VERSION FOR COMPETITION

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import requests
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from src.detection.scam_detector import detect_scam
from src.intelligence.extractor import extract_intelligence
from src.agents.scam_responder import generate_reply
from src.memory.session_store import sessions, create_new_session

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

app = FastAPI()

API_KEY = os.getenv("API_KEY", "TEST_API_KEY")

# Thread pool for non-blocking callbacks
executor = ThreadPoolExecutor(max_workers=20)

def send_guvi_callback_sync(session_id: str, session: dict, serializable_intel: dict) -> bool:
    """Send final results to GUVI - COMPETITION FORMAT"""
    print(f"🚀 Sending GUVI callback for session: {session_id}")
    
    engagement_duration = int(time.time() - session.get("start_time", time.time()))
    
    payload = {
        "sessionId": session_id,
        "status": "completed",
        "scamDetected": session["is_scam"],
        "scamType": session.get("scam_type"),
        "totalMessagesExchanged": session["turns"],
        "extractedIntelligence": serializable_intel,
        "engagementMetrics": {
            "totalMessagesExchanged": session["turns"],
            "engagementDurationSeconds": engagement_duration
        },
        "agentNotes": f"Scam: {session.get('scam_type', 'unknown')}. "
                      f"Confidence: {session['scam_score']}/100. "
                      f"Duration: {engagement_duration}s. "
                      f"Intel: {sum(len(v) for v in serializable_intel.values())} items."
    }
    
    try:
        response = requests.post(GUVI_CALLBACK_URL, json=payload, timeout=2)
        print(f"✅ Callback response: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print(f"⏱️ Callback timeout (>2s) - continuing")
        return False
    except Exception as e:
        print(f"❌ Callback failed: {e}")
        return False


@app.post("/honeypot/message")
async def receive_message(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main endpoint - IMPROVED VERSION
    Key changes:
    1. Passes conversation history to extract_intelligence()
    2. Better intelligence merging
    """
    try:
        # Validate API Key
        if x_api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Invalid API key"}
            )
        
        # Parse request
        data = await request.json()
        
        session_id = data.get("session_id") or data.get("sessionId")
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "sessionId is required"}
            )
        
        message_obj = data.get("message", {})
        message_text = message_obj.get("text", "")
        
        if not message_text:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "message.text is required"}
            )
        
        # Validate message length
        if len(message_text) > 5000:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "message.text too long (max 5000 characters)"}
            )
        
        # Get or create session
        if session_id not in sessions:
            session = create_new_session()
            sessions[session_id] = session
            print(f"🆕 Created new session: {session_id}")
        else:
            session = sessions[session_id]
            print(f"♻️ Using existing session: {session_id}")
        
        # Store message in history
        session["messages"].append({
            "sender": message_obj.get("sender", "scammer"),
            "text": message_text,
            "timestamp": message_obj.get("timestamp")
        })
        
        # Detect scam
        detection_result = detect_scam(message_text)
        is_scam = detection_result["is_scam"]
        scam_score = detection_result["scam_score"]
        scam_type = detection_result["scam_type"]
        
        print(f"🔍 Scam detection: is_scam={is_scam}, score={scam_score}, type={scam_type}")
        
        # Update session
        session["turns"] += 1
        session["is_scam"] = session["is_scam"] or is_scam
        session["scam_score"] = max(session["scam_score"], scam_score)
        
        if scam_type and not session.get("scam_type"):
            session["scam_type"] = scam_type
        
        # ========== CRITICAL FIX: Pass conversation history ==========
        extracted = extract_intelligence(
        text=message_text,
        conversation_history=session["messages"]  # ADD THIS!
        )
        print(f"🕵️ Extracted intelligence: {extracted}")
        
        # Merge extracted intelligence into session
        for key, values in extracted.items():
            if key in session["intelligence"]:
                for val in values:
                    session["intelligence"][key].add(val)
        
        # Convert sets to lists for JSON
        serializable_intel = {
            key: list(session["intelligence"][key])
            for key in session["intelligence"]
        }
        
        # Generate reply - IMPROVED: Use turn count and scam type
        try:
            reply = generate_reply(
                user_message=message_text,
                message_count=session["turns"],
                scam_type=scam_type,  # Pass scam type for better responses
                extracted_intel=serializable_intel  # Pass intel for context
            )
            print(f"🤖 Generated reply: {reply[:50]}...")
        except Exception as e:
            print(f"⚠️ Reply generation error: {e}")
            # Fallback responses based on turn
            fallbacks = [
                "I'm not sure I understand. Can you explain more?",
                "That sounds concerning. How can I verify this is legitimate?",
                "I want to help but I need more details. What exactly do you need?",
                "Can you give me a contact number or email to verify?",
                "Let me think about this and get back to you."
            ]
            reply = fallbacks[min(session["turns"] - 1, len(fallbacks) - 1)]
        
        # Store agent reply
        session["messages"].append({
            "sender": "agent",
            "text": reply,
            "timestamp": None
        })
        
        # Send callback in background (non-blocking)
        should_send_callback = (
            session["is_scam"] 
            and session["turns"] >= 3
            and not session.get("callback_sent", False)
            and len(serializable_intel.get("bankAccounts", []) + 
                   serializable_intel.get("upiIds", []) + 
                   serializable_intel.get("phishingLinks", [])) > 0
        )
        
        if should_send_callback:
            print(f"📞 Scheduling callback for session {session_id}")
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                executor,
                send_guvi_callback_sync,
                session_id,
                session,
                serializable_intel
            )
            session["callback_sent"] = True
            print(f"✅ Callback scheduled (non-blocking)")
        
        # Calculate engagement duration
        engagement_duration = int(time.time() - session.get("start_time", time.time()))
        
        # Return response
        response_data = {
            "status": "success",
            "reply": reply,
            "scamDetected": session["is_scam"],
            "scamScore": session["scam_score"],
            "scamType": session.get("scam_type"),
            "extractedIntelligence": serializable_intel,
            "engagementMetrics": {
                "totalMessagesExchanged": session["turns"],
                "engagementDurationSeconds": engagement_duration,
                "callbackSent": session.get("callback_sent", False)
            },
            "agentNotes": f"Scam type: {session.get('scam_type', 'unknown')}. "
                          f"Confidence: {session['scam_score']}/100. "
                          f"Engaged {engagement_duration}s. "
                          f"Extracted {sum(len(v) for v in serializable_intel.values())} intelligence items."
        }
        
        print(f"✅ Response ready")
        return response_data
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error: {error_trace}")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "trace": error_trace if os.getenv("DEBUG") else None
            }
        )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "sessions": len(sessions),
        "groq_key_present": bool(os.getenv("GROQ_API_KEY"))
    }


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Debug endpoint to view session state"""
    if session_id not in sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    session = sessions[session_id]
    
    return {
        "session_id": session_id,
        "turns": session["turns"],
        "is_scam": session["is_scam"],
        "scam_score": session["scam_score"],
        "scam_type": session.get("scam_type"),
        "callback_sent": session.get("callback_sent", False),
        "intelligence": {
            key: list(values)
            for key, values in session["intelligence"].items()
        },
        "message_count": len(session["messages"])
    }


@app.get("/analytics")
def get_analytics():
    """Analytics endpoint - optimized for speed"""
    intel_breakdown = {}
    total_intel = 0
    total_scams = 0
    
    # Only process last 100 sessions for speed
    recent_sessions = list(sessions.values())[-100:] if len(sessions) > 100 else sessions.values()
    
    for session in recent_sessions:
        if session.get("is_scam"):
            total_scams += 1
        for key, values in session["intelligence"].items():
            if key not in intel_breakdown:
                intel_breakdown[key] = 0
            intel_breakdown[key] += len(values)
            total_intel += len(values)
    
    return {
        "overview": {
            "totalSessions": len(sessions),
            "sessionsAnalyzed": len(recent_sessions),
            "scamsDetected": total_scams,
            "intelligenceItemsExtracted": total_intel
        },
        "intelligenceBreakdown": intel_breakdown
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Agentic AI Honeypot - Competition Optimized",
        "status": "operational",
        "version": "2.1",
        "improvements": [
            "Conversation history extraction",
            "50+ suspicious keywords",
            "9 intelligence types",
            "Multi-turn engagement"
        ]
    }