# ⚙️ Setup Improved Fallback API - Với Custom Endpoint

## ✅ API Credentials Đã Cấu Hình

```
✓ Claude API Key: sk-773e40f46f528675dbe761bd3c11e52a54865401aff048c645427bea8d72f2a3
✓ Claude Endpoint: https://llm.chiasegpu.vn/v1
✓ Claude Model: claude-haiku-4.5
✓ Status: Ready to use
```

## 🚀 Quick Setup (2 phút)

### Bước 1: Copy file

```bash
cp FALLBACK_API_IMPROVED.py utils/fallback_api_v2.py
```

### Bước 2: Update imports trong `utils/chatbot.py`

**Line 13 - Tìm:**

```python
from .claude_fallback_api import get_claude_fallback_api
```

**Thay bằng:**

```python
from .fallback_api_v2 import get_improved_fallback_api
```

**Line 136 - Tìm:**

```python
fallback_api = get_claude_fallback_api()
```

**Thay bằng:**

```python
fallback_api = get_improved_fallback_api()
```

### Bước 3: Khởi động & Test

```bash
python app.py
```

Hoặc test trực tiếp:

```python
from utils.fallback_api_v2 import get_improved_fallback_api

api = get_improved_fallback_api()
result = api.analyze_free_text("Ngành nào phù hợp với tôi?", context="chatbot")
print(result)
```

## 📊 API Configuration

### Claude API (Primary)

- **API Key:** ✓ Already configured
- **Endpoint:** https://llm.chiasegpu.vn/v1
- **Model:** claude-haiku-4.5
- **Status:** ✅ Ready

### Grok API (Fallback)

- **API Key:** Not configured yet (optional)
- **Endpoint:** https://api.x.ai/v1/chat/completions
- **Model:** grok-4-1-fast-reasoning
- **Status:** ⚠️ Optional

## 🔄 Flow Diagram

```
User Question
    ↓
Check Cache (1 giờ)
    ├─ Hit → Return cached response
    └─ Miss → Continue
         ↓
    Claude API + Retry (3x)
         ├─ Success → Return response ✅
         ├─ Timeout → Wait 1s, retry
         ├─ Error → Wait 2s, retry
         └─ Fail 3x → Fallback to Grok
              ↓
         Grok API + Retry (3x)
              ├─ Success → Return response ✅
              └─ Fail 3x → Generic response
                   ↓
              Return error message (no crash)
```

## 🧪 Test Cases

### Test 1: Basic Chat

```python
from utils.fallback_api_v2 import get_improved_fallback_api

api = get_improved_fallback_api()
result = api.analyze_free_text("Tôi thích lập trình", context="chatbot")
print(f"Response: {result['response']}")
print(f"Source: {result['source']}")  # Should be "claude"
```

### Test 2: Form Analysis

```python
result = api.analyze_free_text(
    "Sở thích: Lập trình\nMôn học: Toán, Tin",
    context="form"
)
# Should contain "parsed_data" with JSON structure
if "parsed_data" in result:
    print(f"Top majors: {result['parsed_data']['top_3_majors']}")
```

### Test 3: Cache Hit

```python
# First call - API call made
result1 = api.analyze_free_text("same question")
print(f"Source: {result1['source']}")  # "claude"

# Second call - From cache (instant)
import time
start = time.time()
result2 = api.analyze_free_text("same question")
elapsed = time.time() - start
print(f"Cache hit took: {elapsed:.3f}s")  # Should be < 0.01s
```

### Test 4: Check Logs

```python
import logging
logging.basicConfig(level=logging.INFO)

api = get_improved_fallback_api()
# Will see logs like:
# ✓ Claude client initialized with custom endpoint: https://llm.chiasegpu.vn/v1
# 📤 Calling Claude API (attempt 1/3)...
# ✓ Claude API response received (256 chars)
```

## 🔑 Key Features

✅ **Retry Logic** - 3 lần với exponential backoff (1s, 2s, 4s)  
✅ **Dual API** - Claude (primary) → Grok (fallback)  
✅ **Custom Endpoint** - Sử dụng llm.chiasegpu.vn thay vì official  
✅ **Smart Cache** - Cache 1 giờ  
✅ **Never Crash** - Luôn trả response  
✅ **Detailed Logging** - Chi tiết debugging

## ⚙️ Configuration Options

### Customize Retry

```python
# Trong FALLBACK_API_IMPROVED.py
MAX_RETRIES = 5        # Thay từ 3 sang 5
RETRY_DELAY = 2        # Thay từ 1 sang 2
```

### Customize Cache

```python
# Trong FALLBACK_API_IMPROVED.py
CACHE_TTL_SECONDS = 7200  # Thay từ 3600 (1h) sang 7200 (2h)
```

### Customize Model

```python
# Trong FALLBACK_API_IMPROVED.py
CLAUDE_MODEL = "claude-opus-4-1"  # Thay model nếu cần
```

## 🔍 Debugging

### View Logs

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Cache Stats

```python
api = get_improved_fallback_api()
stats = api.get_cache_stats()
print(f"Total cached: {stats['total_entries']}")
print(f"Valid entries: {stats['valid_entries']}")
print(f"Expired: {stats['expired_entries']}")
```

### Clear Cache

```python
api.clear_cache()  # Xóa tất cả cache
```

## 📞 Common Issues

### Issue 1: "Claude client not available"

**Cause:** `anthropic` library not installed  
**Fix:**

```bash
pip install anthropic
```

### Issue 2: Slow response (>5s)

**Cause:** Network issue or API server slow  
**Solution:** Check logs to see retry attempts, increase MAX_RETRIES

### Issue 3: API key invalid

**Cause:** API key expired or wrong  
**Fix:** Update API key in file or `.env`

## ✨ What's New vs Old

| Feature         | Old   | New                 |
| --------------- | ----- | ------------------- |
| Retry           | ❌    | ✅ 3x with backoff  |
| Fallback        | ❌    | ✅ Claude → Grok    |
| Custom Endpoint | ❌    | ✅ llm.chiasegpu.vn |
| Error Handling  | Basic | Advanced            |
| Logging         | Basic | Detailed            |
| Never Crash     | ❌    | ✅                  |

## 🎯 Expected Behavior

✅ **Normal Case (Claude works):**

```
Request → Claude API (attempt 1) → Success → Response
Time: ~2 seconds
```

✅ **Timeout Case (Claude slow):**

```
Request → Claude timeout → Wait 1s → Retry → Success
Time: ~3 seconds
```

✅ **API Down Case (Both fail):**

```
Request → Claude fail 3x → Grok fail 3x → Generic response
Time: ~10 seconds
Status: User still gets helpful message!
```

## 📝 Summary

- ✅ Claude API ready với custom endpoint
- ✅ Retry logic + dual fallback implemented
- ✅ Never crash - always returns response
- ✅ Smart caching for performance
- ✅ Detailed logging for debugging

**Ready to use! Copy to utils/ and update imports.** 🚀
