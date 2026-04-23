# 🔧 Hướng Dẫn Sửa API Fallback Lỗi của Botchat

## 📋 Vấn Đề Chính

Code fallback API hiện tại có các lỗi:

1. **❌ Không có retry logic** - API gọi 1 lần, fail là lỗi
2. **❌ Error handling yếu** - Timeout/failure không xử lý tốt
3. **❌ Không có dual fallback** - Chỉ dùng Claude hoặc Grok, không có fallback
4. **❌ Response format không nhất quán** - Gây confusion giữa các API

## ✅ Giải Pháp

Tôi đã tạo file **`FALLBACK_API_IMPROVED.py`** với các cải tiến:

### 1️⃣ **Dual API Support (Claude + Grok)**

```python
# Try Claude first
response_text = self._call_claude_api_with_retry(prompt)
if response_text:
    return success_response

# Fallback to Grok
response_text = self._call_grok_api_with_retry(prompt)
if response_text:
    return success_response

# Final fallback - generic response
return error_response
```

### 2️⃣ **Retry Logic với Exponential Backoff**

```python
for attempt in range(MAX_RETRIES):  # 3 lần thử
    try:
        # Call API
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (2 ** attempt))  # 1s, 2s, 4s
```

### 3️⃣ **Better Error Handling**

- ✅ Timeout exception → Retry
- ✅ HTTP error → Retry
- ✅ Connection error → Retry
- ✅ Log tất cả lỗi chi tiết

### 4️⃣ **Response Validation**

```python
# Check if response is valid
if "choices" in data and len(data["choices"]) > 0:
    content = data["choices"][0]["message"]["content"]
    return content
```

## 🚀 Cách Sử Dụng

### Bước 1: Thay Thế File

```bash
# Backup file cũ
cp utils/claude_fallback_api.py utils/claude_fallback_api.py.bak

# Sao chép file mới
cp FALLBACK_API_IMPROVED.py utils/fallback_api_improved.py
```

### Bước 2: Update trong `utils/chatbot.py`

```python
# Cũ
from .claude_fallback_api import get_claude_fallback_api

# Mới
from .fallback_api_improved import get_improved_fallback_api

# Trong _get_fallback_response()
fallback_api = get_improved_fallback_api()
result = fallback_api.analyze_free_text(text, context="chatbot")
```

### Bước 3: Cấu Hình Environment

Đảm bảo `.env` có:

```env
# Claude API
ANTHROPIC_API_KEY=sk_your_claude_key_here

# Grok API
GROK_API_KEY=sk_your_grok_key_here
```

### Bước 4: Test

```python
from utils.fallback_api_improved import get_improved_fallback_api

# Test
api = get_improved_fallback_api()
result = api.analyze_free_text("Ngành nào phù hợp?", context="chatbot")
print(result)
```

## 📊 Comparison: Cũ vs Mới

| Tiêu Chí            | Cũ ❌           | Mới ✅                |
| ------------------- | --------------- | --------------------- |
| Retry Logic         | ❌ Không        | ✅ 3 lần với backoff  |
| Dual API            | ❌ Chỉ Claude   | ✅ Claude + Grok      |
| Error Handling      | ❌ Cơ bản       | ✅ Chi tiết           |
| Timeout             | ❌ Một lần thôi | ✅ Retry 3 lần        |
| Logging             | ⚠️ Cơ bản       | ✅ Chi tiết với emoji |
| Response Validation | ⚠️ Cơ bản       | ✅ Kiểm tra kỹ lưỡng  |

## 🧪 Test Scenarios

### Test 1: API Timeout (Claude)

```python
# Claude timeout → Fallback to Grok
result = api.analyze_free_text("test question")
# Kỳ vọng: Grok response được trả về ✅
```

### Test 2: Both APIs Fail

```python
# Cả Claude và Grok đều fail
# Kỳ vọng: error response được trả về (không crash)
```

### Test 3: Cache Hit

```python
result1 = api.analyze_free_text("same question")
result2 = api.analyze_free_text("same question")  # Từ cache
# Kỳ vọng: result2 trả về ngay lập tức
```

### Test 4: Form Context (JSON Response)

```python
result = api.analyze_free_text("...", context="form")
# Kỳ vọng: Có "parsed_data" field với JSON structure
```

## 📝 Key Features

✅ **Automatic Retry** - Tự động thử lại nếu API fail  
✅ **Dual Fallback** - Claude → Grok → Generic response  
✅ **Smart Cache** - Cache 1 giờ để tránh gọi API lặp lại  
✅ **Better Logging** - Log chi tiết mỗi lần thử  
✅ **Error Recovery** - Không crash, luôn trả về response  
✅ **Response Validation** - Kiểm tra response format

## 🔍 Debugging

### View Logs

```python
import logging
logging.basicConfig(level=logging.INFO)

# Sẽ thấy output like:
# ✓ Claude client initialized
# 📤 Calling Claude API (attempt 1/3)...
# ⚠ Claude API timeout (attempt 1)
# 📤 Calling Grok API (attempt 1/3)...
# ✓ Grok API response received (256 chars)
```

### Check Cache Stats

```python
api = get_improved_fallback_api()
stats = api.get_cache_stats()
print(stats)
# Output: {
#   "total_entries": 5,
#   "valid_entries": 4,
#   "expired_entries": 1
# }
```

## 🚨 Configuration

### Timeout Settings

```python
# Mỗi API call timeout sau 30 giây
timeout=30.0
```

### Retry Settings

```python
MAX_RETRIES = 3        # Thử 3 lần
RETRY_DELAY = 1        # Bắt đầu delay 1 giây
# Sẽ retry với delay: 1s, 2s, 4s
```

### Cache Settings

```python
CACHE_TTL_SECONDS = 3600  # Cache 1 giờ
```

## 💡 Best Practices

1. **Luôn có API key** - Không chạy được nếu không có ANTHROPIC_API_KEY hoặc GROK_API_KEY
2. **Monitor logs** - Xem logs để biết API nào được dùng
3. **Test fallback** - Thử test với API key sai để thấy fallback hoạt động
4. **Clear cache** - Gọi `api.clear_cache()` nếu cần reset

## 📦 Requirements

```
anthropic>=0.10.0
requests>=2.31.0
python-dotenv>=1.0.0
```

Đã có trong `requirements.txt` rồi!

## ✨ Summary

**Old Code**: Gọi API 1 lần → Fail → Error  
**New Code**: Retry Claude 3 lần → Fail → Retry Grok 3 lần → Fail → Generic response

Giờ botchat sẽ **luôn** trả về response hữu ích thay vì bị lỗi!

---

**📞 Cần help?** Check `FALLBACK_API_IMPROVED.py` để xem implementation chi tiết!
