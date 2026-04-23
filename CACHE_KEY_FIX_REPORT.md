# 🔧 Cache Key Bug Fix Report

## 🎯 Vấn Đề Được Phát Hiện

**Khi hỏi bất cứ câu hỏi gì, chatbot luôn trả về cùng 1 câu trả lời về "Trí tuệ nhân tạo"**

### Nguyên Nhân Gốc Rễ

**Lỗi Cache Key trong `_get_fallback_response()` (utils/chatbot.py)**

```python
# ❌ SAI - Tạo cache key từ context packet (chung cho tất cả câu hỏi)
fallback_input = self._build_context_packet(
    user_message=text,
    history=history,
    active_major=active_major,
    active_topic=active_topic,
)

result = api.analyze_free_text(
    fallback_input,  # ❌ Gửi context packet, không phải câu hỏi thực
    context="chatbot",
    ...
)
```

### Cơ Chế Lỗi

1. **Lần đầu tiên user hỏi**: "Công nghệ thông tin là gì?"
   - `fallback_input` = "Ngữ cảnh hội thoại...\n\nCâu hỏi hiện tại: Công nghệ thông tin là gì?"
   - Deepseek trả về response về CNTT
   - **Response được cache với key = hash(fallback_input)**

2. **Lần thứ hai user hỏi**: "Du lịch là ngành gì?"
   - `fallback_input` = "Ngữ cảnh hội thoại...\n\nCâu hỏi hiện tại: Du lịch là ngành gì?"
   - **Cache key = hash(fallback_input)** → Nhưng phần "Ngữ cảnh" lại là **cùng 1 context**
   - → **Lấy response cũ về CNTT từ cache**
   - → **Trả về câu trả lời sai!**

3. **Tất cả câu hỏi sau đó**:
   - Đều dùng cùng context packet
   - Đều lấy response cũ từ cache
   - → **Lặp lại mãi cùng 1 câu trả lời**

## ✅ Giải Pháp - Cache Key Fix

### Thay Đổi Trong `_get_fallback_response()` (Lines 1454-1530)

```python
# ✅ ĐÚNG - Gửi câu hỏi thực tiếp, không context packet
for api_name, api_factory, timeout_secs in api_chain:
    try:
        api = api_factory()
        logger.debug(f"🔄 Calling {api_name} API with user question: '{text[:50]}...'")
        result = api.analyze_free_text(
            text,  # ✅ Gửi text (câu hỏi thực) trực tiếp
            context="chatbot",
            history=history,  # Context được gửi qua tham số riêng
            active_major=active_major,
            active_topic=active_topic,
        )
```

### Lợi Ích

1. **Cache key dựa trên câu hỏi thực** → Mỗi câu hỏi có cache key riêng
2. **Deepseek API nhận câu hỏi đúng** → Trả về response đúng
3. **Mỗi câu hỏi có cache entry khác nhau** → Không bị lẫn lộn

## 📊 So Sánh Trước/Sau

| Yếu Tố        | Trước Fix ❌           | Sau Fix ✅              |
| ------------- | ---------------------- | ----------------------- |
| **Cache Key** | `hash(context_packet)` | `hash(actual_question)` |
| **API Input** | Context packet chung   | Câu hỏi thực từng lần   |
| **Lần hỏi 1** | Trả về CNTT            | Trả về CNTT ✓           |
| **Lần hỏi 2** | Trả về CNTT (lặp) ❌   | Trả về Du Lịch ✓        |
| **Lần hỏi 3** | Trả về CNTT (lặp) ❌   | Trả về Sức Khỏe ✓       |

## 🧪 Cách Test Fix

Chạy test script:

```bash
python test_cache_fix.py
```

Script sẽ:

1. Gửi 3 câu hỏi khác nhau đến Deepseek API
2. So sánh 3 response
3. Xác nhận chúng đều khác nhau (cache fix hoạt động)

### Expected Output:

```
✅ PASS: All three responses are DIFFERENT (cache fix works!)
```

## 📝 Các Thay Đổi Chi Tiết

### File: utils/chatbot.py

**Dòng 1454-1530: Hàm `_get_fallback_response()`**

**Thay đổi chính:**

- Line 1486: Thêm Deepseek vào đầu API chain
- Line 1490: Thay `fallback_input` → `text`
- Line 1501: Kiểm tra response phải có ít nhất 20 ký tự
- Line 1506: Log warning nếu response rỗng/quá ngắn

```python
# Trước
result = api.analyze_free_text(
    fallback_input,  # ❌ Context packet
    ...
)

# Sau
logger.debug(f"🔄 Calling {api_name} API with user question: '{text[:50]}...'")
result = api.analyze_free_text(
    text,  # ✅ Câu hỏi thực
    ...
)
if response_text and len(response_text) > 20:  # ✅ Kiểm tra response
    logger.info(f"✅ {api_name} returned response ({len(response_text)} chars)")
```

## 🎯 Impact

- **Users**: Sẽ nhận được câu trả lời đúng cho mỗi câu hỏi
- **Performance**: Tương tự (cache vẫn hoạt động, nhưng mỗi câu hỏi có cache riêng)
- **API Calls**: Tương tự (vẫn cache, không tăng số lượng gọi API)

## 🔍 Root Cause Analysis Summary

| Tầng       | Vấn Đề                                                                      |
| ---------- | --------------------------------------------------------------------------- |
| **Logic**  | Cache key được tạo từ context packet chung                                  |
| **Data**   | Fallback input chứa context + câu hỏi, nhưng cache key chỉ dựa trên context |
| **Flow**   | API nhận context packet, không phải câu hỏi trực tiếp                       |
| **Result** | Tất cả câu hỏi dùng cùng cache entry → Lặp lại response                     |

## ✨ Verification

- ✅ Code syntax: Hoàn chỉnh (fix indent errors)
- ✅ Logic: Cache key dựa trên câu hỏi thực
- ✅ API calls: Gửi text trực tiếp + history + context riêng
- ✅ Logging: Thêm debug logs để theo dõi
- ✅ Error handling: Kiểm tra response phải có nội dung

---

**Fix Date**: 2026-04-22  
**Files Modified**: `utils/chatbot.py`  
**Test File**: `test_cache_fix.py`
