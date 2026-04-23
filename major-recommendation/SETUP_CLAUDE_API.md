# Hướng dẫn setup Anthropic Claude API Key

## ⚠️ Vấn đề hiện tại

API key được cung cấp không hợp lệ:

```
Error: "invalid x-api-key"
Status: 401 Authentication Error
```

---

## ✅ Giải pháp

### Bước 1: Lấy API key hợp lệ từ Anthropic

1. Truy cập: https://console.anthropic.com/
2. Đăng nhập hoặc tạo tài khoản Anthropic
3. Tìm section **"API Keys"**
4. Click **"Create Key"**
5. Copy key mới (format: `sk-ant-xxxxxxx...`)

### Bước 2: Cập nhật file `.env`

1. Mở file `.env` trong project
2. Cập nhật API key:

```env
ANTHROPIC_API_KEY=sk-ant-[YOUR_NEW_API_KEY_HERE]
```

3. Lưu file (không commit vào git)

### Bước 3: Test lại

```bash
python test_chatbot.py
```

---

## 🔍 Kiểm tra kết quả

Nếu hoạt động, bạn sẽ thấy:

```
📤 Calling Claude API (haiku-4.5)...
✓ Claude API response received (xxx chars)
```

Thay vì:

```
⚠ Claude API error: Error code: 401 - invalid x-api-key
```

---

## 📝 Ghi chú quan trọng

- **API Key format**: `sk-ant-` (Anthropic) không phải `sk-` (Grok)
- **File `.env`** không được commit vào git (đã config trong `.gitignore`)
- **Cài đặt dependencies**: `pip install -r requirements.txt`
- Bao gồm: `anthropic`, `python-dotenv`, `requests`, v.v.

---

## 🔄 Flow hoạt động

Chatbot sử dụng **hybrid approach**:

1. **Greeting** (Xin chào) → Trả lời ngay
2. **Pattern Matching** (Công nghệ, kinh doanh) → Trả lời từ template
3. **TF-IDF Model** (confidence ≥ 0.5) → Trả lời từ model ML
4. **Claude API Fallback** (confidence < 0.5) → Gọi Claude Haiku 4.5

---

## 💡 Tương lai

- Nếu model của bạn đủ tốt, có thể tắt Claude API để tiết kiệm chi phí
- Cơ chế caching 1 giờ giảm số lần gọi API

---

## 🐛 Troubleshooting

| Lỗi                              | Nguyên nhân                   | Giải pháp                             |
| -------------------------------- | ----------------------------- | ------------------------------------- |
| `invalid x-api-key`              | API key sai/hết hạn           | Lấy key mới từ console.anthropic.com  |
| `authentication_error`           | Thiếu API key hoặc sai format | Kiểm tra file `.env`                  |
| `ModuleNotFoundError: anthropic` | Chưa cài anthropic            | Chạy `pip install anthropic`          |
| `.env` không được load           | Chưa gọi `load_dotenv()`      | Đã fix trong `claude_fallback_api.py` |

---

Liên hệ hoặc check docs: https://docs.anthropic.com/
