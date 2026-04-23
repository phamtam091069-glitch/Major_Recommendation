# 🚀 REPLIT QUICK START (5 PHÚT XONG)

## ✅ Files đã chuẩn bị sẵn

Bạn không cần làm gì cả, tất cả files đã được tạo:

- ✅ `.replit` - Cấu hình chạy
- ✅ `requirements.txt` - Dependencies (thêm gunicorn)
- ✅ `app.py` - Sửa host 0.0.0.0 + port
- ✅ `.env.replit` - Template variables
- ✅ `replit_init.py` - Auto-generate model
- ✅ `REPLIT_DEPLOYMENT_GUIDE.md` - Chi tiết đầy đủ

---

## 🚀 BƯỚC DEPLOY (Cực nhanh)

### 1️⃣ Tạo Replit Project

- Truy cập: https://replit.com
- Click **"Create"** → **"New Replit"**
- Chọn **"Python"**
- Upload/paste files từ project này

### 2️⃣ Thêm Secrets (Environment Variables)

- Click 🔒 icon bên trái
- Thêm 3 secrets:
  ```
  ANTHROPIC_API_KEY = sk-ant-YOUR_KEY
  OPENAI_API_KEY = sk-YOUR_KEY
  SECRET_KEY = any-random-string
  ```

### 3️⃣ Click "Run" ▶️

- Replit tự động:
  - Cài dependencies
  - Chạy `python app.py`
  - Tạo public URL

### 4️⃣ Lấy URL công khai

```
https://major-recommendation-USERNAME.replit.dev
```

**Done! 🎉 Web của bạn bây giờ là PUBLIC + REALTIME 24/7**

---

## 📝 Config Files (Đã sửa sẵn)

### `.replit` - Chạy Flask

```
run = "python app.py"
modules = ["python-3.10"]
```

### `requirements.txt` - Thêm gunicorn

```
Flask==3.0.3
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.1
scipy==1.13.1
joblib==1.4.2
requests==2.31.0
python-dotenv==1.0.0
anthropic>=0.25.0
openai>=1.0.0
gunicorn==21.2.0  ← ADDED
```

### `app.py` - Host 0.0.0.0

```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## ✨ Kết quả

| Tiêu chí       | Kết quả             |
| -------------- | ------------------- |
| **URL**        | Public & cố định ✅ |
| **Realtime**   | 24/7 hoạt động ✅   |
| **Chi phí**    | $0 miễn phí ✅      |
| **Setup time** | 5 phút ✅           |

---

## 🔧 Troubleshooting

**Lỗi: "Model not found"**

- Mở console → Chạy:
  ```bash
  python data/generate_balanced_students.py
  python train_model.py
  ```

**Lỗi: "API key not found"**

- Check Secrets (🔒) có đủ key?
- Reload: Ctrl+Shift+R

**Web chậm?**

- Bình thường (free tier: 0.5 CPU)
- Mất 5-10s cho request đầu tiên

---

## 📞 Cần Chi tiết?

Xem file: **REPLIT_DEPLOYMENT_GUIDE.md** (hướng dẫn đầy đủ)

---

**Chúc deploy thành công! 🎊**
