# 🕵️ Agentic AI Honeypot System

An AI-powered honeypot that detects scam messages, engages scammers in realistic conversations, and extracts intelligence without revealing detection.

Built for GUVI Hackathon 2026.

## 🎯 Features

- ✅ **Scam Detection** - Rule-based detection with confidence scoring
- ✅ **AI Agent Engagement** - Groq LLM-powered realistic victim persona
- ✅ **Multi-Turn Conversations** - Handles conversation history and context
- ✅ **Intelligence Extraction** - Captures UPI IDs, bank accounts, phone numbers, phishing links
- ✅ **Automatic Reporting** - Sends results to evaluation endpoint
- ✅ **API Authentication** - Secured with API key validation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Groq API Key ([Get one here](https://console.groq.com/))

### Local Setup

```bash
# Clone repository
git clone <your-repo-url>
cd honeypot-project

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-groq-api-key"
export API_KEY="TEST_API_KEY"

# Run server
uvicorn src.api.server:app --reload

# Test
python test_honeypot.py
```

### Deploy to Render.com

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed deployment instructions.

## 📡 API Endpoints

### POST /honeypot/message

Main endpoint for scam detection and engagement.

**Headers:**
```
Content-Type: application/json
x-api-key: YOUR_API_KEY
```

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked. Verify now.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": []
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Why is my account blocked?",
  "scamDetected": true,
  "scamScore": 80,
  "scamType": "impersonation_scam",
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["urgent", "verify"]
  },
  "engagementMetrics": {
    "totalMessagesExchanged": 1,
    "callbackSent": false
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "sessions": 0,
  "groq_key_present": true
}
```

## 🏗️ Project Structure

```
.
├── src/
│   ├── api/
│   │   └── server.py           # FastAPI server
│   ├── agents/
│   │   └── scam_responder.py   # AI agent logic
│   ├── detection/
│   │   └── scam_detector.py    # Scam detection rules
│   ├── intelligence/
│   │   └── extractor.py        # Intelligence extraction
│   └── memory/
│       └── session_store.py    # Session management
├── test_honeypot.py            # Test suite
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (local)
└── README.md                   # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_honeypot.py
```

Tests include:
- Health check
- Scam detection
- Multi-turn conversations
- API key validation
- Intelligence extraction

## 🔒 Security

- API key authentication required
- No real sensitive data stored
- Agent never reveals actual credentials
- Safe intelligence extraction patterns

## 📊 Scam Detection

Detection based on:
- Dominant triggers (OTP, password, CVV requests)
- Intent patterns (verify + bank, click + link)
- Urgency indicators (immediate, urgent, now)
- Scoring system (0-100)

Scam types identified:
- Payment scams (UPI, transfers)
- OTP/credential phishing
- Phishing links
- Bank impersonation

## 🤖 AI Agent Behavior

The agent:
- Acts as a confused but cooperative victim
- Never provides real credentials
- Asks verification questions
- Delays and deflects sensitive requests
- Extracts information through conversation
- Maintains realistic human-like responses

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Groq API key for LLM |
| `API_KEY` | No | `TEST_API_KEY` | API authentication key |
| `DEBUG` | No | `false` | Show error traces |

## 🎯 Hackathon Requirements

✅ Detects scam intent  
✅ Activates autonomous AI agent  
✅ Maintains believable human persona  
✅ Handles multi-turn conversations  
✅ Extracts actionable intelligence  
✅ Returns structured JSON response  
✅ API key authentication  
✅ Sends callback to evaluation endpoint  

## 📈 Performance

- Response time: < 2 seconds (with Groq)
- Scam detection: Rule-based (instant)
- Intelligence extraction: Regex-based (instant)
- Multi-session support: In-memory storage

## 🤝 Contributing

This is a hackathon project. For improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - Built for GUVI Hackathon 2026

## 👨‍💻 Author

Created for GUVI Agentic AI Honeypot Buildathon

## 🙏 Acknowledgments

- Groq for LLM API
- FastAPI framework
- GUVI for organizing the hackathon
