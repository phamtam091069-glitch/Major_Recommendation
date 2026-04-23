# 🚀 PYTHONANYWHERE DEPLOYMENT GUIDE (Chi tiết)

## 📋 BƯỚC 1: Tạo PythonAnywhere Account

### 1.1 Đăng ký

- Truy cập: https://www.pythonanywhere.com
- Click "Pricing"
- Chọn **"Beginner (Free)"** hoặc **"Hacker"**
- Điền email, password
- Verify email

### 1.2 Đăng nhập

- Vào trang chủ
- Dashboard sẽ appear

---

## 📦 BƯỚC 2: Upload Project

### Option A: Git (Khuyến nghị)

1. **Push code lên GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Major recommendation project"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/major-recommendation.git
   git push -u origin main
   ```

2. **Trên PythonAnywhere:**
   - Dashboard → **Bash console**
   - Chạy:
     ```bash
     git clone https://github.com/YOUR_USERNAME/major-recommendation.git
     cd major-recommendation
     ```

### Option B: Upload Files

1. Dashboard → **Files**
2. Tạo folder: `major-recommendation`
3. Upload files

---

## 🐍 BƯỚC 3: Tạo Virtual Environment

```bash
# Trên PythonAnywhere Bash console:
mkvirtualenv --python=/usr/bin/python3.10 major-rec
pip install -r requirements.txt
```

### Xác nhận:

```bash
which python
# Output: /home/username/.virtualenvs/major-rec/bin/python
```

---

## 🌐 BƯỚC 4: Tạo Web App

1. Dashboard → **Web** tab (bên trái)
2. Click **"+ Add a new web app"**
3. Chọn domain: `username.pythonanywhere.com`
4. Chọn **"Manual configuration"**
5. Chọn **Python 3.10**
6. Ghi nhớ đường dẫn (sẽ là `/home/username/major-recommendation`)

---

## ⚙️ BƯỚC 5: Config WSGI

1. Dashboard → **Web** tab
2. Click vào web app
3. Scroll xuống → **WSGI configuration file**
4. Click link để edit file
5. **Clear tất cả** rồi paste code này:

```python
import sys
import os

# Project path - CHANGE username
project_home = '/home/username/major-recommendation'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment - CHANGE username
activate_this = '/home/username/.virtualenvs/major-rec/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Environment variables
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')

# Import Flask app
from app import app as application
```

6. **Sửa 2 chỗ `username`** với username thực tế
7. Click "Save"

---

## 🔑 BƯỚC 6: Set Environment Variables

1. Dashboard → **Web** tab
2. Click web app
3. Scroll xuống → **Environment variables**
4. Click "Add"
5. Thêm lần lượt:
   ```
   ANTHROPIC_API_KEY: sk-ant-YOUR_ACTUAL_KEY
   OPENAI_API_KEY: sk-YOUR_ACTUAL_KEY
   SECRET_KEY: any-random-secret-string
   ```
6. Save

---

## 🔄 BƯỚC 7: Reload Web App

1. Dashboard → **Web** tab
2. Click web app
3. Scroll lên → Click **"Reload username.pythonanywhere.com"**
4. Chờ ~10-30 giây

---

## ✅ Test Web App

### URL:

```
https://username.pythonanywhere.com
```

### Các endpoint:

- **Homepage**: `https://username.pythonanywhere.com/`
- **Chatbot**: `https://username.pythonanywhere.com/chatbot`
- **Health**: `https://username.pythonanywhere.com/health`

---

## 🔧 Troubleshooting

### ❌ "500 Internal Server Error"

**Nguyên nhân:** Code error hoặc config sai

**Fix:**

1. Check error log: Dashboard → **Web** tab → **Error log**
2. Xem lỗi cụ thể
3. Sửa trong file editor
4. Reload web app

### ❌ "ImportError: No module named 'flask'"

**Nguyên nhân:** Virtual environment không activate

**Fix:**

1. Check WSGI file có activate venv không?
2. Chạy lại: `pip install -r requirements.txt`
3. Reload web app

### ❌ "Module not found: 'app'"

**Nguyên nhân:** Đường dẫn project sai

**Fix:**

1. Check đường dẫn trong WSGI file
2. Verify file `app.py` tồn tại
3. Sửa WSGI config
4. Reload

### ❌ "API key not found"

**Nguyên nhân:** Environment variables chưa set

**Fix:**

1. Check environment variables đã add?
2. Reload web app (để load lại env vars)

---

## 📊 Monitoring & Logs

### View Logs:

- Dashboard → **Web** tab
- **Error log**: Errors
- **Server log**: Debug info
- **Access log**: Requests

### View Code Changes:

- Dashboard → **Files**
- Edit file directly
- Auto-save

---

## 🚀 Live Website

**Done!** Your web is now live at:

```
https://username.pythonanywhere.com
```

Share this URL với bất kỳ ai để test!

---

## 💡 Tips

1. **First deploy có thể chậm** (cài dependencies)
2. **Reload after code change** (WSGI server)
3. **Check error log khi có problem**
4. **Virtual env phải activate trong WSGI**
5. **Environment variables cần reload để active**

---

**Chúc deploy thành công! 🎊**
