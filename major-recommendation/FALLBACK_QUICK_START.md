# API Fallback - Quick Start Guide

## ⚠️ DEPRECATED - GROK API REMOVED

This guide is kept for historical reference. GROK API support has been removed from this project.

---

## ⚡ 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Check if Everything Works

```bash
python app.py
# Look for: Claude API initialization messages
```

### 3. Test the Chatbot

```bash
# In another terminal:
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi thích AI và machine learning"}'

# Response:
{
    "reply": "AI-generated response",
    "source": "model",
    "confidence": 0.75
}
```

## 🎯 How It Works

### Automatic Processing

- **Chatbot**: Uses Claude API for responses
- **Form**: Processes inputs with confidence scoring
- **Both**: Uses retry logic for reliability

### Three Layers of Response

```
1. Model Match (High confidence) → Use model result
2. Claude API → Use Claude for uncertain cases
3. Generic Response (API fail) → Friendly message
```

## 📝 Common Use Cases

### Case 1: Known Interest in Chatbot

**User asks:** "I love computer science, which major is best?"

**What happens:**

1. Model TF-IDF matching confidence: 0.85 (high)
2. Direct response from model
3. User gets immediate answer

### Case 2: Unusual Input

**User enters:** "so_thich_chinh": "blockchain"

**What happens:**

1. Model processes with lower confidence
2. System provides helpful response
3. User gets guidance

### Case 3: Error Handling

**If API fails:**

1. Retry logic automatically engages
2. Generic helpful message returned
3. User experience maintained

## 🔧 Key Files

| File                    | Purpose                         |
| ----------------------- | ------------------------------- |
| `utils/chatbot.py`      | Chatbot with API integration    |
| `utils/predictor.py`    | Model-based prediction          |
| `app.py`                | Flask app with routes           |
| `API_FALLBACK_GUIDE.md` | Full documentation (deprecated) |

## 🧪 Quick Tests

### Test 1: Basic Chatbot

```python
from utils.chatbot import MajorChatbot

chatbot = MajorChatbot(predictor)

# Ask a question
response = chatbot.chat("What major suits programming?")
print(response['reply'])
print(f"Confidence: {response['confidence']}")
```

### Test 2: API Reliability

```python
# System handles API failures gracefully
# No crashes, always returns helpful response
response = chatbot.chat("test question")
print(response['success'])  # Always True or returns default
```

## ⚙️ Customization

### Change Confidence Threshold

```python
# In utils/chatbot.py
self.CONFIDENCE_THRESHOLD = 0.6  # Was 0.5
```

### Adjust API Timeout

```python
# In your API client
timeout = 30  # seconds
```

## 📊 Monitoring

### Check Logs

```bash
python app.py 2>&1 | grep -i "claude\|api\|error"

# Look for:
# Claude API initialized
# Response generated
# Error handling if needed
```

## 🚀 Performance

- **Direct response**: ~1ms (model match)
- **API call**: ~2-3s average
- **Timeout**: 30s maximum
- **Always responds**: No hanging

## 🆘 Troubleshooting

### API not responding

```
Check internet connection
Verify API configuration in .env
Review logs for error messages
```

### Slow responses

```
Monitor API latency (typically 2-3s)
Check system resources
Review network connectivity
```

## 📚 Documentation

- Main README: `README.md`
- Claude API setup: `SETUP_CLAUDE_API.md`
- Error handling: `FIX_GUIDE.md`

## 🎓 What Changed

**Removed:**

- ❌ Grok API support
- ❌ Grok configuration
- ❌ Grok-specific caching

**Maintained:**

- ✅ Claude API integration
- ✅ All chatbot features
- ✅ Error handling
- ✅ Prediction endpoints

---

**Version**: 2.0 (Updated without Grok) | **Status**: ✅ Ready to Use
