# src/api/server.py - EMERGENCY FIX VERSION

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import requests
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.detection.scam_detector import detect_scam
from src.intelligence.extractor import extract_intelligence
from src.agents.scam_responder import generate_reply
from src.memory.session_store import sessions, create_new_session

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

app = FastAPI()

API_KEY = os.getenv("API_KEY", "TEST_API_KEY")

# Thread pool for non-blocking callbacks
executor = ThreadPoolExecutor(max_workers=3)

def send_guvi_callback_sync(session_id: str, session: dict, serializable_intel: dict) -> bool:
    """Send final results to GUVI - runs in background thread"""
    print(f"🚀 Sending GUVI callback for session: {session_id}")
    
    payload = {
        "sessionId": session_id,
        "scamDetected": session["is_scam"],
        "totalMessagesExchanged": session["turns"],
        "extractedIntelligence": serializable_intel,
        "agentNotes": f"Scam classified as {session.get('scam_type', 'unknown')}. Score: {session['scam_score']}"
    }
    
    try:
        # CRITICAL: Very short timeout, fire-and-forget
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
    Main endpoint to receive messages and engage scammers
    """
    try:
        # Validate API Key
        if x_api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Invalid API key"}
            )
        
        # Parse request body
        data = await request.json()
        
        # Extract sessionId (support both formats)
        session_id = data.get("session_id") or data.get("sessionId")
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "sessionId is required"}
            )
        
        # Extract message
        message_obj = data.get("message", {})
        message_text = message_obj.get("text", "")
        
        if not message_text:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "message.text is required"}
            )
        
        # Extract conversation history (optional)
        conversation_history = data.get("conversationHistory", [])
        
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
        
        # Update session with detection results
        session["turns"] += 1
        session["is_scam"] = session["is_scam"] or is_scam
        session["scam_score"] = max(session["scam_score"], scam_score)
        
        if scam_type and not session.get("scam_type"):
            session["scam_type"] = scam_type
        
        # Extract intelligence from message
        extracted = extract_intelligence(message_text)
        print(f"🕵️ Extracted intelligence: {extracted}")
        
        # Merge extracted intelligence into session
        for key, values in extracted.items():
            if key in session["intelligence"]:
                session["intelligence"][key].update(values)
        
        # Convert sets to lists for JSON serialization
        serializable_intel = {
            key: list(values)
            for key, values in session["intelligence"].items()
        }
        
        # Generate AI reply
        try:
            reply = generate_reply(
                user_message=message_text,
                message_count=session["turns"]
            )
            print(f"🤖 Generated reply: {reply[:50]}...")
        except Exception as e:
            print(f"⚠️ Groq API error: {e}")
            reply = "I'm not sure I understand. Could you explain more?"
        
        # Store agent reply in history
        session["messages"].append({
            "sender": "agent",
            "text": reply,
            "timestamp": None
        })
        
        # CRITICAL FIX: Send callback in background (non-blocking)
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
            # Fire callback in background thread - DON'T WAIT FOR IT
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                executor,
                send_guvi_callback_sync,
                session_id,
                session,
                serializable_intel
            )
            session["callback_sent"] = True  # Mark immediately
            print(f"✅ Callback scheduled (non-blocking)")
        
        # Return response immediately (don't wait for callback)
        response_data = {
            "status": "success",
            "reply": reply,
            "scamDetected": session["is_scam"],
            "scamScore": session["scam_score"],
            "scamType": session.get("scam_type"),
            "extractedIntelligence": serializable_intel,
            "engagementMetrics": {
                "totalMessagesExchanged": session["turns"],
                "callbackSent": session.get("callback_sent", False)
            }
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
    
    # Convert sets to lists for JSON
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
    """Analytics endpoint"""
    intel_breakdown = {}
    total_intel = 0
    total_scams = 0
    
    for session in sessions.values():
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
            "scamsDetected": total_scams,
            "intelligenceItemsExtracted": total_intel
        },
        "intelligenceBreakdown": intel_breakdown
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Agentic AI Honeypot",
        "status": "operational",
        "version": "2.0"
    }