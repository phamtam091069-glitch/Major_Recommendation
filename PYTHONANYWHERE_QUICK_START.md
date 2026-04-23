# 🚀 PYTHONANYWHERE QUICK START (10 PHÚT XONG)

## ✅ Tóm tắt PythonAnywhere

**PythonAnywhere là gì?**

- Hosting trực tiếp cho Python web apps
- Setup WSGI (production-ready)
- URL: `https://username.pythonanywhere.com`
- Free tier có đủ cho demo/learning

---

## 🚀 DEPLOY TRONG 10 PHÚT

### 1️⃣ Tạo PythonAnywhere Account

```
https://www.pythonanywhere.com
→ Click "Sign up"
→ Free account
→ Verify email
```

### 2️⃣ Upload Project Files

**Option A: Git (recommended)**

```bash
# Trên PythonAnywhere console:
git clone https://github.com/YOUR_USERNAME/major-recommendation.git
cd major-recommendation
```

**Option B: Web editor**

- Dashboard → Files
- Upload từng file

### 3️⃣ Tạo Virtual Environment

```bash
# Trên PythonAnywhere Bash console:
mkvirtualenv --python=/usr/bin/python3.10 major-rec
pip install -r requirements.txt
```

### 4️⃣ Tạo Web App

- Dashboard → Web tab
- Click "Add a new web app"
- Choose "Manual configuration"
- Python 3.10
- Ghi nhớ đường dẫn project

### 5️⃣ Config WSGI

- Edit WSGI configuration file
- Copy code từ `wsgi_config.py` vào đó
- Sửa đường dẫn project (nếu khác)

### 6️⃣ Set Environment Variables

- Web app settings → Environment variables
- Thêm:
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  OPENAI_API_KEY=sk-...
  SECRET_KEY=your-secret-key
  ```

### 7️⃣ Reload Web App

- Web tab → Click "Reload"
- Chờ ~10 giây

### ✅ DONE!

```
https://username.pythonanywhere.com
```

---

## 📝 Config Files

### `wsgi_config.py` - Đã chuẩn bị

```python
import sys
import os

# Project path
project_home = '/home/username/major-recommendation'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Virtual environment
activate_this = '/home/username/.virtualenvs/major-rec/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Set environment variables
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')

# Import Flask app
from app import app as application
```

### `requirements.txt` - Không thay đổi

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
```

---

## 🔧 Troubleshooting

**Lỗi: "Module not found"**

- Check virtual environment activated
- Run: `pip install -r requirements.txt`
- Reload web app

**Lỗi: "API key not found"**

- Check environment variables set
- Reload web app

**Lỗi: "ImportError: cannot import name 'app'"**

- Check WSGI file path correct
- Check `app.py` at project root

**Web chậm/404 error**

- Check WSGI config correct
- Check error log: Dashboard → Logs

---

## 📞 Cần Chi tiết?

Xem: `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` (hướng dẫn đầy đủ)

**Chúc deploy thành công! 🎊**
