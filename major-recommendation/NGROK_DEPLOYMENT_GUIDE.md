# 🚀 HƯỚNG DẪN DEPLOY VỚI NGROK

## ✅ CHATBOT LỖI ĐÃ ĐƯỢC SỬA

**Thay đổi thực hiện:**

- ✅ QA patterns giới hạn xuống top 3 ngành (thay vì hơn 3)
- ✅ Thêm helper function `_limit_to_top3_majors()` để filter response
- ✅ Áp dụng filter vào cả OpenAI & Claude fallback response

**Files đã sửa:**

- `utils/chatbot.py` - Giới hạn tất cả responses chỉ hiển thị top 3 ngành

---

## 📋 GIAI ĐOẠN 1: CÀI ĐẶT NGROK (5 PHÚT)

### Bước 1: Download Ngrok

- Vào https://ngrok.com/download
- Download phiên bản **Windows**
- Giải nén vào thư mục (ví dụ: `C:\ngrok`)

### Bước 2: Tạo Tài Khoản Ngrok (Miễn Phí)

- Vào https://ngrok.com
- Click **Sign Up**
- Điền email & password
- Xác minh email

### Bước 3: Lấy Authtoken

1. Đăng nhập Ngrok
2. Vào **Getting Started** → **Your Authtoken**
3. Copy token (dạng: `1234567890_abc123xyz...`)

### Bước 4: Setup Ngrok Authtoken

**Cách 1: Dùng Command Prompt (Nhanh nhất)**

```bash
ngrok authtoken YOUR_AUTHTOKEN_HERE
```

**Cách 2: Thêm vào PATH (Để dùng từ bất kỳ đâu)**

1. Mở **Settings** → **Environment Variables**
2. Click **Edit the system environment variables**
3. Click **Environment Variables** button
4. Thêm folder ngrok vào **PATH**

---

## 🎯 GIAI ĐOẠN 2: CHẠY FLASK APP LOCALLY (2 PHÚT)

### Bước 1: Mở Command Prompt & Chạy App

```bash
# Đi đến thư mục dự án
cd c:\Users\huyen\Downloads\major-recommendation

# Activate virtual environment (nếu có)
venv\Scripts\activate

# Cài đặt dependencies (nếu chưa)
pip install -r requirements.txt

# Chạy Flask app
python app.py
```

**Kết quả:**

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

✅ **App đang chạy trên local!** Mở http://127.0.0.1:5000 để kiểm tra

---

## 🌐 GIAI ĐOẠN 3: PUBLIC VỚI NGROK (1 PHÚT)

### Bước 1: Mở Command Prompt Mới

⚠️ **KHÔNG đóng cái CMD đang chạy Flask!**

Mở CMD thứ 2, chạy:

```bash
ngrok http 5000
```

### Bước 2: Copy Link Public

Bạn sẽ thấy:

```
ngrok by @inconshreveable

Session Status                online
Account                       your-email@gmail.com
Version                        3.x.x
Region                         United States
Latency                        -
Web Interface                  http://127.0.0.1:4040
Forwarding                     https://abc123def456.ngrok.io -> http://localhost:5000
Forwarding                     http://abc123def456.ngrok.io -> http://localhost:5000
```

🎉 **Link public của bạn là:** `https://abc123def456.ngrok.io`

---

## ✨ GIAI ĐOẠN 4: TEST & CHIA SẺ (5 PHÚT)

### Bước 1: Test App

- Mở link ngrok trong trình duyệt: `https://abc123def456.ngrok.io`
- Điền form → Xem kết quả
- Test chatbot → Kiểm tra chỉ có top 3 ngành (✅ LỖI ĐÃ SỬA)

### Bước 2: Chia Sẻ Link

- Copy link: `https://abc123def456.ngrok.io`
- Chia sẻ cho ai cũng được dùng
- Họ có thể dùng từ bất kỳ thiết bị nào

### Bước 3: Xem Traffic (Optional)

- Mở http://127.0.0.1:4040 để xem request/response

---

## 🔄 QUẢN LÝ NGROK SESSION

### Restart Ngrok (Nếu cần)

```bash
# Đóng ngrok (Ctrl+C)
# Chạy lại:
ngrok http 5000
```

**⚠️ Lưu ý:** Link sẽ thay đổi mỗi lần restart!

### Tắt Ngrok

```bash
Ctrl+C
```

### Xem Tất Cả Sessions

```bash
ngrok sessions
```

---

## 🐛 TROUBLESHOOTING

| Lỗi                           | Giải Pháp                                                       |
| ----------------------------- | --------------------------------------------------------------- |
| **"ngrok not found"**         | Ngrok chưa thêm vào PATH, chạy từ thư mục ngrok hoặc setup PATH |
| **"Address already in use"**  | Port 5000 đang được dùng, kill process hoặc dùng port khác      |
| **"Connection refused"**      | Flask app không chạy, chạy lại `python app.py`                  |
| **Link bị timeout**           | Ngrok free plan có timeout 8h, chạy lại để lấy link mới         |
| **Chatbot hiển thị >3 ngành** | ❌ Lỗi này đã sửa trong version này!                            |

---

## 📊 QUICK REFERENCE

```
Terminal 1:
$ cd major-recommendation
$ venv\Scripts\activate
$ python app.py
→ http://127.0.0.1:5000

Terminal 2:
$ ngrok http 5000
→ https://abc123def456.ngrok.io ✅

Copy link → Share → Test ✨
```

---

## 📌 CHÚ Ý QUAN TRỌNG

✅ **Đã sửa:**

- Chatbot giới hạn chỉ hiển thị top 3 ngành (không còn dòng dư)
- Tất cả QA patterns đã cập nhật
- Fallback API response được filter

⏰ **Thời gian:**

- Ngrok session sống 8 giờ (free plan)
- Link thay đổi mỗi khi restart

🔐 **Bảo mật:**

- Ai có link thì vào được
- Để private hơn, upgrade Pro plan ($7/tháng)

---

## 🎓 NEXT STEPS

1. **Deploy vĩnh viễn:** Dùng Render.com (miễn phí, link cố định)
2. **Thêm database:** Lưu feedback vào PostgreSQL
3. **Optimize:** Reduce model size để deploy nhanh hơn
4. **Monitor:** Setup logging & error tracking

---

**Bạn đã sẵn sàng! 🚀**

Hãy chạy 2 terminal & enjoy! 🎉
