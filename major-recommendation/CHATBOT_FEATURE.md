# 🤖 Chatbot Tư Vấn Ngành Học - Feature Guide

## Overview

Tính năng chatbot mới cho phép người dùng chat tự do để tìm hiểu thêm về các ngành học. Chatbot sử dụng model đã train kết hợp với fallback API để trả lời các câu hỏi của người dùng.

## Tính Năng

### 1. Floating Button (Nút Nổi)

- 📍 **Vị trí**: Góc phải dưới của màn hình
- 🎨 **Biểu tượng**: 💬 (chat bubble)
- ✨ **Effects**: Hover scale + gradient shadow
- 🎯 **Hành động**: Click để mở chatbot

### 2. Chat Modal

- 📱 **Responsive**: Tích hợp tốt trên desktop và mobile
- 🎨 **Design**: Đẹp với gradient, animation, scrollbar custom
- 📊 **Messages**: Hiển thị lịch sử chat trong session
- 🚪 **Toggle**: Form ẩn khi mở chatbot, hiện lại khi đóng

### 3. Chatbot Intelligence

Chatbot sử dụng 3 cấp độ xử lý:

#### Level 1: Greeting Detection

- Nhận diện các lời chào đơn giản
- Confidence: 1.0 (chắc chắn)
- Ví dụ: "Xin chào", "Hi", "Hello"

#### Level 2: Pattern Matching

- Match với các mẫu câu hỏi đã định nghĩa
- Confidence: 0.95
- Ví dụ: "Công nghệ là gì?", "Ngành kinh doanh"
- Các pattern bao gồm: công nghệ, kỹ thuật, kinh doanh, ngôn ngữ, sức khỏe, du lịch, giáo dục, thiết kế

#### Level 3: TF-IDF Model Matching

- Sử dụng TF-IDF + Cosine Similarity từ model đã train
- So sánh với mô tả các ngành học
- Confidence: 0.5 - 1.0 (tùy độ tương đồng)
- Trả về thông tin ngành phù hợp nhất

#### Level 4: Fallback Response

- Khi model không đủ tự tin (confidence < 0.5)
- Gợi ý người dùng điều gì có thể làm
- Confidence: 0.0 (không chắc chắn)

## Architecture

### Backend (`utils/chatbot.py`)

```python
class MajorChatbot:
    - __init__(predictor)  # Khởi tạo với predictor
    - chat(user_message)   # Xử lý tin nhắn người dùng
    - _is_greeting()       # Kiểm tra lời chào
    - _check_pattern_match()  # Kiểm tra pattern
    - _get_tfidf_response()   # TF-IDF matching
    - _get_fallback_response()  # Fallback
```

### API Endpoint (`app.py`)

```
POST /chat
Request: { "message": "Người dùng hỏi gì?" }
Response: {
    "reply": "Trả lời từ chatbot",
    "source": "greeting|pattern|model|fallback",
    "confidence": 0.95
}
```

### Frontend (`static/script.js`)

```javascript
-toggleChat(open) - // Mở/đóng chatbot
  sendChatMessage() - // Gửi tin nhắn
  addMessage(text, sender) - // Thêm bubble vào UI
  escapeHtml(text); // Escape HTML (bảo mật)
```

### Styling (`static/style.css`)

```css
- .chat-float-btn         // Floating button
- .chat-modal             // Chat modal container
- .chat-bubble.user/.bot  // Message bubbles
- .chat-input-area        // Input area
- @media (max-width: 640px) // Responsive
```

## User Flow

```
1. User clicks floating button 💬
   ↓
2. Chat modal opens, form ẩn
   ↓
3. Initial greeting message displays
   ↓
4. User types question & press Enter / click Send
   ↓
5. Message sent to /chat endpoint
   ↓
6. Backend processes:
   - Check greeting → Pattern → TF-IDF → Fallback
   ↓
7. Response returns with source & confidence
   ↓
8. Message bubble appears in chat
   ↓
9. User can continue chatting or click "Quay về form"
   ↓
10. Chat history clears, form displays again
```

## Response Examples

### Greeting

```
User: "Xin chào"
Bot: "Xin chào! 👋 Mình là chatbot tư vấn ngành học..."
Source: greeting
Confidence: 1.0
```

### Pattern Match

```
User: "Công nghệ là gì?"
Bot: "Công nghệ là một lĩnh vực rất tiềm năng..."
Source: pattern
Confidence: 0.95
```

### TF-IDF Model

```
User: "Em muốn học ngành về máy tính"
Bot: "Dựa trên câu hỏi, mình gợi ý ngành Công nghệ thông tin..."
Source: model
Confidence: 0.75
```

### Fallback

```
User: "Thời tiết hôm nay sao?"
Bot: "Mình không hoàn toàn chắc chắn... Bạn có thể..."
Source: fallback
Confidence: 0.0
```

## Chat History

- ✅ Lưu trong memory của session hiện tại
- ❌ Xóa khi user click "Quay về form"
- ❌ Xóa khi refresh trang
- 💾 Không lưu vào database (yêu cầu của user)

## Customization

### Thêm Greeting Pattern

```python
# utils/chatbot.py - MajorChatbot.__init__()
self.greeting_responses = {
    "xin chào": "Xin chào!...",
    "hi": "Hi!...",
    "your_pattern": "Your response"
}
```

### Thêm QA Pattern

```python
self.qa_patterns = {
    "pattern_keyword": "Response text",
}
```

### Thay đổi TF-IDF Threshold

```python
# utils/chatbot.py
self.CONFIDENCE_THRESHOLD = 0.5  # Thay đổi giá trị
```

### Integrate với External API

```python
# utils/chatbot.py - _get_fallback_response()
# Thêm code để gọi OpenAI/Gemini/Groq API tại đây
def _get_fallback_response(self, text: str):
    # Call external API
    response = call_openai_api(text)
    return response
```

## Testing

### Run Chatbot Test

```bash
python test_chatbot.py
```

Output:

```
============================================================
TESTING CHATBOT FUNCTIONALITY
============================================================

1. Loading predictor...
   ✓ Predictor loaded successfully

2. Creating chatbot instance...
   ✓ Chatbot created successfully

3. Testing chatbot responses:
   ✓ Message 1: Greeting
   ✓ Message 2: Pattern match
   ✓ Message 3: Model matching
   ✓ Message 4: Fallback

✓ CHATBOT TEST PASSED
```

## Troubleshooting

### Chatbot không hiện

- Check console (F12) cho errors
- Verify `/chat` endpoint working: `curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"test"}'`
- Check model ready: Visit `/health`

### Chat không gửi được

- Verify form data là JSON
- Check network tab trong browser DevTools
- Verify message không rỗng

### Response quá chậm

- Check server logs
- Verify model loaded: `python test_chatbot.py`
- Optimize TF-IDF threshold nếu cần

## Future Enhancements

1. 🌐 **Integrate External API**
   - OpenAI GPT-4
   - Google Gemini
   - Groq (fast inference)

2. 💾 **Persistent Chat History**
   - Lưu vào database
   - Retrieve previous conversations

3. 🔄 **Context Awareness**
   - Nhớ thông tin người dùng
   - Multi-turn conversations

4. 📊 **Analytics**
   - Track chat statistics
   - Popular questions
   - User satisfaction

5. 🎓 **Educational Mode**
   - Deeper explanations
   - Course recommendations
   - Career paths

6. 🌍 **Multi-language**
   - English support
   - Chinese, Japanese support

## Files Changed

```
✅ Created:
  - utils/chatbot.py (250+ lines)
  - test_chatbot.py (40+ lines)
  - CHATBOT_FEATURE.md (this file)

✏️ Modified:
  - app.py (+30 lines for /chat endpoint)
  - templates/index.html (+40 lines for UI)
  - static/style.css (+180 lines for styling)
  - static/script.js (+100 lines for functionality)
```

## Summary

Chatbot tư vấn ngành học mới giúp người dùng:

- ✨ Chat tự do về các ngành học
- 🤖 Nhận gợi ý từ AI model đã train
- 🎯 Khám phá ngành phù hợp
- 💬 Trải nghiệm interactive

Với fallback API, chatbot có thể mở rộng để trả lời các câu hỏi ngoài phạm vi dataset trong tương lai!
