# 🚀 HƯỚNG DẪN DEPLOY LÊN REPLIT (Chi tiết từng bước)

## ✅ HOÀN TOÀN MIỄN PHÍ + REALTIME 24/7

---

## 📋 BƯỚC 1: Chuẩn bị trên máy local

### 1.1 Kiểm tra files cần thiết:

```bash
cd /path/to/major-recommendation

# Kiểm tra các file sau:
ls -la .replit                    # ✅ File config Replit
ls -la requirements.txt            # ✅ Dependencies
ls -la app.py                      # ✅ Main app
ls -la data/majors_profiles.json  # ✅ Major data
```

### 1.2 Files đã được chuẩn bị:

- ✅ `.replit` - Cấu hình Replit
- ✅ `requirements.txt` - Thêm gunicorn
- ✅ `app.py` - Cập nhật host 0.0.0.0
- ✅ `.env.replit` - Template biến môi trường

---

## 🌐 BƯỚC 2: Tạo Replit Project

### Option A: Import từ GitHub (KHUYẾN NGHỊ)

1. **Fork project lên GitHub:**

   ```bash
   # Trên máy local:
   git init
   git add .
   git commit -m "Initial commit for Replit deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/major-recommendation.git
   git push -u origin main
   ```

2. **Trên Replit (replit.com):**
   - Click **"Create"** → **"Import from GitHub"**
   - Dán URL: `https://github.com/YOUR_USERNAME/major-recommendation`
   - Click **"Import"**

### Option B: Upload trực tiếp

1. Truy cập: https://replit.com
2. Click **"Create"** → **"New Replit"**
3. Chọn **"Python"**
4. Tạm thời skip, sau upload files

---

## 🔑 BƯỚC 3: Thêm Environment Variables

### 3.1 Trên Replit:

1. **Bên trái màn hình → Biểu tượng 🔒 "Secrets"**
2. **Click "Add new secret"** (hoặc **"New Secret"**)

### 3.2 Thêm từng biến:

```
Key: ANTHROPIC_API_KEY
Value: sk-ant-YOUR_ACTUAL_KEY_HERE
→ Click Save

Key: OPENAI_API_KEY
Value: sk-YOUR_ACTUAL_KEY_HERE
→ Click Save

Key: SECRET_KEY
Value: your-random-secret-string
→ Click Save
```

### 3.3 Kiểm tra:

- Click 🔒 lại → Xem có 3 secrets?
- ✅ ANTHROPIC_API_KEY
- ✅ OPENAI_API_KEY
- ✅ SECRET_KEY

---

## 📦 BƯỚC 4: Cài đặt Dependencies

Replit sẽ tự động detect `requirements.txt` và cài.

**Hoặc cài manual:**

```bash
# Trong console Replit:
pip install -r requirements.txt
```

---

## 🎯 BƯỚC 5: Chạy & Deploy

### 5.1 Trên Replit:

1. **Click nút "Run" ▶️** (bên phải màn hình)
2. Replit sẽ:
   - Cài dependencies từ `requirements.txt`
   - Chạy `python app.py` (từ `.replit`)
   - Tạo public URL

### 5.2 Chờ output:

```
* Running on http://0.0.0.0:5000
* Replit automatically exposed this port at: https://major-recommendation-USERNAME.replit.dev
```

### 5.3 Lấy Public URL:

- Bên phải màn hình sẽ show: `Open in new tab` 🔗
- Hoặc tìm URL ở console output
- **URL format:** `https://major-recommendation-USERNAME.replit.dev`

---

## ✨ BƯỚC 6: Kiểm tra Hoạt động

### 6.1 Test Homepage:

```
Truy cập: https://major-recommendation-USERNAME.replit.dev/
Bạn sẽ thấy: Form nhập hồ sơ
```

### 6.2 Test Chatbot:

```
Truy cập: https://major-recommendation-USERNAME.replit.dev/chatbot
Bạn sẽ thấy: Giao diện chatbot
```

### 6.3 Test API:

```bash
# Health check:
curl https://major-recommendation-USERNAME.replit.dev/health

# Kết quả:
{"status": "ok", "model_ready": true}
```

### 6.4 Test Prediction:

```bash
curl -X POST https://major-recommendation-USERNAME.replit.dev/predict \
  -H "Content-Type: application/json" \
  -d '{
    "so_thich_chinh": "Công nghệ",
    "mon_hoc_yeu_thich": "Toán",
    "ky_nang_noi_bat": "Tư duy logic",
    "tinh_cach": "Kỷ luật",
    "moi_truong_lam_viec_mong_muon": "Kỹ thuật",
    "muc_tieu_nghe_nghiep": "Phát triển chuyên môn",
    "mo_ta_ban_than": "Em thích lập trình",
    "dinh_huong_tuong_lai": "Em muốn làm kỹ sư phần mềm"
  }'
```

---

## 🔧 Troubleshooting

### ❌ Lỗi: "Model not found"

**Nguyên nhân:** Model chưa được generate

**Giải pháp:**

1. Mở console Replit
2. Chạy:

```bash
python data/generate_balanced_students.py
python train_model.py
```

3. Sau đó click "Run" lại

### ❌ Lỗi: "API key not found"

**Giải pháp:**

1. Check lại Secrets (🔒) có đủ key?
2. Kiểm tra key value không có typo?
3. Reload Replit: **Ctrl+Shift+R**

### ❌ Lỗi: "Module not found"

**Giải pháp:**

1. Console:

```bash
pip install -r requirements.txt
```

2. Click "Run" lại

### ❌ Web chậm / Timeout

**Giải pháp:**

1. Replit free tier: 0.5 CPU + 0.5GB RAM (bình thường)
2. Có thể mất 5-10s cho request đầu tiên
3. Là bình thường, không cần lo

---

## 📊 Replit Free Tier Specs

| Tiêu chí     | Giá trị                   |
| ------------ | ------------------------- |
| **Chi phí**  | $0 (miễn phí vĩnh viễn)   |
| **CPU**      | 0.5 vCPU                  |
| **RAM**      | 0.5 GB                    |
| **Storage**  | 2 GB                      |
| **Uptime**   | 24/7 (nếu project active) |
| **URL**      | Cố định & vĩnh viễn       |
| **HTTPS**    | ✅ Có                     |
| **Realtime** | ✅ 24/7 hoạt động         |

---

## 🎉 Kết quả

✅ **Web Public URL:** `https://major-recommendation-USERNAME.replit.dev`
✅ **Realtime 24/7:** Không cần lo, luôn hoạt động
✅ **Chi phí:** Hoàn toàn miễn phí
✅ **Setup:** Chỉ ~5-10 phút

---

## 📞 Support & Tips

### Để web không bị "sleep" (free tier):

- Replit sẽ keep web alive nếu bạn thường xuyên access
- Hoặc setup external monitoring tool

### Để tăng performance:

- Upgrade lên Replit Pro ($7/tháng)
- Hoặc dùng VPS DigitalOcean ($4-5/tháng)

### Để backup code:

```bash
# Trên Replit console:
git remote add github https://github.com/YOUR_USERNAME/major-recommendation.git
git push github main
```

---

## 🚀 Tiếp theo

Sau khi deploy xong:

1. **Share URL:**

   ```
   Bạn có thể share URL này cho bất kỳ ai
   https://major-recommendation-USERNAME.replit.dev
   ```

2. **Monitor logs:**
   - Bên dưới editor console sẽ show logs realtime
   - Xem các request, error, etc.

3. **Update code:**
   - Edit file trên Replit → Tự động reload (nếu debug mode)
   - Hoặc click "Stop" rồi "Run" lại

---

**Chúc bạn deploy thành công! 🎊**
