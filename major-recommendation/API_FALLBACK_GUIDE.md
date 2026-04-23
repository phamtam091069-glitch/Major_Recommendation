# API Fallback Integration Guide

## 📋 Overview

⚠️ **DEPRECATED**: The Grok API fallback system has been removed. This file is kept for historical reference.

The system now uses **Claude API** for all requests with retry logic and error handling.

## 🎯 Features

✅ **Out-of-Dataset Detection**: Automatically detects when user input doesn't match training data
✅ **Grok AI Fallback**: Uses Grok-4-1-Fast-Reasoning for intelligent recommendations
✅ **Smart Caching**: Caches results for 1 hour to reduce API calls
✅ **Error Handling**: Gracefully falls back to heuristic responses if API fails
✅ **Logging**: Comprehensive logging of fallback triggers and API calls
✅ **Seamless Integration**: Works transparently with existing chatbot and prediction endpoints

## 🔧 Architecture

### Files Added/Modified

```
utils/
├── fallback_api.py          (NEW) Grok API handler
├── predictor.py             (MODIFIED) Import fallback handler
├── chatbot.py               (MODIFIED) Use Grok for fallback responses
└── __init__.py              (existing)

app.py                        (MODIFIED) Import fallback API
requirements.txt              (MODIFIED) Add requests library
```

### Component Structure

```
┌─────────────────────────────────────────────────────┐
│                   User Input                        │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Chatbot / Form       │
         │  (app.py)             │
         └───────────┬───────────┘
                     │
        ┌────────────▼────────────┐
        │  Model-based matching   │
        │  (TF-IDF, confidence)   │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  Confidence >= 0.5?     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  YES                    │  NO
        │  Use Model Result       │  Trigger Fallback
        │                         │
        │                    ┌────▼──────────────┐
        │                    │ Check Cache       │
        │                    └────┬──────────────┘
        │                         │
        │                    ┌────▼──────────────┐
        │                    │ Cache Hit?        │
        │                    └────┬──────────────┘
        │                         │
        │        ┌────────────────▼───────────────┐
        │        │  YES              NO           │
        │        │  Return Cached  Call Grok API  │
        │        │  Result         (Grok4-Fast)   │
        │        └────────┬──────────┬────────────┘
        │                 │          │
        │                 └──────┬───┘
        └─────────────────────────▼───────────┐
                    Return Result
        ┌───────────────────────────────────┐
        │  Format & Return to Frontend      │
        └───────────────────────────────────┘
```

## 📡 API Configuration

### Grok API Details

- **Provider**: xai-api (X.AI)
- **Model**: grok-4-1-fast-reasoning
- **API Endpoint**: https://api.x.ai/v1/chat/completions
- **API Key**: Embedded in `utils/fallback_api.py`
- **Timeout**: 30 seconds
- **Cache TTL**: 1 hour (3600 seconds)

### Request/Response Example

**Fallback for Chatbot (context="chatbot"):**

```python
# Input
user_message = "Tôi thích lập trình và thích giải quyết vấn đề logic"

# Grok Prompt
"""
Trả lời câu hỏi của học sinh về các ngành đại học và lộ trình học tập:

Câu hỏi/Thông tin: Tôi thích lập trình và thích giải quyết vấn đề logic

Yêu cầu:
1. Trả lời một cách thân thiện, khuyến khích
2. Nếu hỏi về ngành cụ thể, giải thích chi tiết
3. Nếu hỏi chung chung, gợi ý cách xác định ngành phù hợp
4. Đề xuất bước tiếp theo (như điền form chi tiết)

Trả về câu trả lời tự nhiên (Tiếng Việt), không cần JSON.
"""

# Expected Output
"Dựa trên sở thích lập trình và giải quyết vấn đề logic của bạn, bạn rất phù hợp với các ngành như..."
```

**Fallback for Form (context="form"):**

```python
# Input
user_profile = {
    "so_thich_chinh": "robotics",  # Out of dataset
    "mon_hoc_yeu_thich": "tin hoc",
    # ... other fields
}

# Expected Output JSON
{
  "strengths": ["Lập trình", "Tư duy logic", "Giải quyết vấn đề"],
  "top_3_majors": [
    {
      "major": "Công nghệ thông tin",
      "reason": "Yêu cầu kỹ năng lập trình và tư duy logic",
      "fit_score": 88
    },
    {
      "major": "Kỹ thuật cơ khí",
      "reason": "Phù hợp với robotics và giải quyết vấn đề",
      "fit_score": 82
    },
    {
      "major": "Tự động hóa",
      "reason": "Kết hợp lập trình và robotics",
      "fit_score": 79
    }
  ],
  "overall_recommendation": "..."
}
```

## 🚀 Usage

### For Chatbot Integration

The chatbot automatically uses fallback when model confidence is low:

```python
from utils.chatbot import MajorChatbot

chatbot = MajorChatbot(predictor)
response = chatbot.chat("My question about majors")

# Response object:
{
    "reply": "AI-generated response from Grok API or model",
    "source": "fallback" | "model" | "pattern" | "greeting",
    "confidence": 0.45  # Low confidence triggers fallback
}
```

### Direct Fallback API Usage

```python
from utils.fallback_api import get_fallback_api

fallback_api = get_fallback_api()

# For free-text analysis
result = fallback_api.analyze_free_text(
    user_text="My interests and skills",
    context="chatbot"  # or "form"
)

# For structured profile analysis
result = fallback_api.get_major_recommendation(
    user_profile={
        "so_thich_chinh": "custom_interest",
        "mo_ta_ban_than": "My description"
    }
)

# Cache management
stats = fallback_api.get_cache_stats()
fallback_api.clear_cache()
```

## 📊 Endpoints

### Existing Endpoints (Fallback Enabled)

- **POST `/predict`** - Form submission with fallback on low confidence
- **POST `/chat`** - Chatbot with automatic fallback for unknown questions
- **GET `/health`** - Health check endpoint

### Response Examples

**Chatbot with Fallback:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ngành nào phù hợp với robotics?"}'

# Response (if low confidence)
{
    "reply": "[Grok AI response about robotics-related majors]",
    "source": "fallback",
    "confidence": 0.35
}
```

## 🔍 Logging

The fallback system includes comprehensive logging:

```
✓ GrokFallbackAPI initialized
✓ Cache hit for: user_text_chatbot
📤 Calling Grok API...
✓ Grok API response received (256 chars)
✓ Successfully parsed Grok JSON response
✓ Cached result for: user_text_form
⚠ Grok API timeout (30s)
✗ Lỗi khi lưu feedback: [error message]
```

## ⚙️ Configuration

### Environment Variables (Optional)

For future security improvements, you can modify `utils/fallback_api.py`:

```python
import os

GROK_API_KEY = os.getenv("GROK_API_KEY", "your-key-here")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL", 3600))
```

### Customization

**Change confidence threshold:**

```python
# In utils/chatbot.py
self.CONFIDENCE_THRESHOLD = 0.6  # Default: 0.5
```

**Adjust cache TTL:**

```python
# In utils/fallback_api.py
CACHE_TTL_SECONDS = 7200  # 2 hours instead of 1
```

**Modify Grok model:**

```python
# In utils/fallback_api.py
GROK_MODEL = "grok-4-1-vision"  # Or other Grok models
```

## 🧪 Testing

### Manual Test Cases

**Test 1: Chatbot with Out-of-Dataset Input**

```python
chatbot.chat("I'm interested in blockchain and Web3")
# Expected: Fallback triggers (confidence < 0.5)
# Response: Grok AI generates recommendation
```

**Test 2: Prediction with Unusual Values**

```bash
POST /predict
{
    "so_thich_chinh": "quantum_computing",  # Not in dataset
    "mon_hoc_yeu_thich": "tin hoc",
    ...
}
# Expected: Fallback API provides recommendations
```

**Test 3: Cache Hit**

```python
# First call - API call made
result1 = fallback_api.analyze_free_text("test input")

# Second call - From cache (immediate)
result2 = fallback_api.analyze_free_text("test input")

# Check cache stats
stats = fallback_api.get_cache_stats()
print(stats)  # {total_entries: 1, valid_entries: 1, ...}
```

**Test 4: API Failure Handling**

```python
# Simulate API timeout
# Expected: Fallback to generic response without error
result = fallback_api.analyze_free_text("test")
print(result["success"])  # False
```

## 📈 Performance

- **Cache Hit**: ~1ms response time
- **API Call**: ~2-3s average (depends on Grok latency)
- **Fallback Timeout**: 30s maximum
- **Database Size**: Negligible (in-memory cache)

## 🛡️ Error Handling

The system handles various failure scenarios:

1. **API Timeout** → Generic fallback response
2. **Connection Error** → Logged and generic response
3. **Invalid JSON Response** → Log warning, use raw response
4. **Model Not Ready** → Return 500 error with message

## 🚨 Security Considerations

⚠️ **API Key Management**: Currently hardcoded for demo. For production:

```python
# Use environment variables
import os
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Or use .env file
from dotenv import load_dotenv
load_dotenv()
```

✅ **Input Validation**: All user inputs are validated
✅ **Rate Limiting**: Consider adding for production
✅ **Logging**: Sensitive data is not logged

## 📚 Documentation Files

- `API_FALLBACK_GUIDE.md` - This file
- `README.md` - Main project documentation
- Code comments in `utils/fallback_api.py`

## 🔄 Integration Checklist

- [x] Created `utils/fallback_api.py` with GrokFallbackAPI class
- [x] Updated `utils/chatbot.py` to use Grok fallback
- [x] Updated `utils/predictor.py` with logging
- [x] Updated `app.py` to import fallback handler
- [x] Added `requests` to `requirements.txt`
- [x] Implemented caching mechanism
- [x] Added comprehensive error handling
- [x] Created documentation

## 🎓 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Test chatbot**: Try asking unusual questions
3. **Monitor logs**: Watch for fallback triggers
4. **Adjust thresholds**: Tune confidence levels based on results
5. **Scale up**: Consider rate limiting and caching strategies

## 📞 Support

For issues or questions:

1. Check logs for error messages
2. Review `utils/fallback_api.py` for implementation details
3. Test with sample inputs manually
4. Verify Grok API key and endpoint are correct

---

**Version**: 1.0  
**Last Updated**: 2026-04-15  
**Status**: ✅ Production Ready
