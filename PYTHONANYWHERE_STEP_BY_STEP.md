# 🚀 PythonAnywhere Deployment - Step By Step Guide

**Username:** `tranvinh028`  
**Domain:** `tranvinh028.pythonanywhere.com`  
**GitHub Repo:** `https://github.com/phamtam091069-glitch/Major_Recommendation.git`

---

## ✅ Prerequisites Checklist

- [x] GitHub Repository Created & Code Pushed
- [x] PythonAnywhere Account: tranvinh028
- [x] API Keys Available:
  - Deepseek: `sk-880b704d61334b5a9e9ba34a18d0a537`
  - Claude #1: `sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da`
  - Claude #2: `sk-52eb797508a111c6f62cd677d23b5feed662f5d94390c86c34e14f3b0ec52176`

---

## 📋 STEP 1: Clone Repository (2-3 minutes)

### 1.1 Open Bash Console

- Login to PythonAnywhere: https://www.pythonanywhere.com
- Dashboard → **Bash console** (bottom left)

### 1.2 Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone from GitHub
git clone https://github.com/phamtam091069-glitch/Major_Recommendation.git

# Navigate into project
cd Major_Recommendation

# Verify files exist
ls -la
# Should see: app.py, requirements.txt, templates/, utils/, etc.
```

### 1.3 Verify

```bash
pwd
# Should output: /home/tranvinh028/Major_Recommendation
```

✅ **Step 1 Complete**

---

## 🐍 STEP 2: Create Virtual Environment (3-5 minutes)

### 2.1 Create Virtual Environment

```bash
# Create venv named 'major-rec'
mkvirtualenv --python=/usr/bin/python3.10 major-rec

# You should see: (major-rec) in your prompt
```

### 2.2 Install Dependencies

```bash
# Activate venv (should be auto-activated after mkvirtualenv)
workon major-rec

# Install from requirements.txt
pip install -r requirements.txt

# This will install:
# - Flask==3.0.3
# - pandas==2.2.2
# - scikit-learn==1.5.1
# - anthropic>=0.25.0
# - requests==2.31.0
# - etc.
```

### 2.3 Verify Installation

```bash
python --version
# Should show: Python 3.10.x

which python
# Should show: /home/tranvinh028/.virtualenvs/major-rec/bin/python

pip list | grep Flask
# Should show: Flask 3.0.3
```

✅ **Step 2 Complete**

---

## 🌐 STEP 3: Create Web App (2 minutes)

### 3.1 Go to Web Tab

- PythonAnywhere Dashboard
- Click **"Web"** tab (left sidebar)

### 3.2 Add New Web App

- Click **"+ Add a new web app"**
- Choose domain: `tranvinh028.pythonanywhere.com` (auto-filled)
- Click **"Next"**

### 3.3 Select Framework

- Choose **"Manual configuration"** (NOT "Flask" preset)
- Click **"Next"**

### 3.4 Select Python Version

- Select **"Python 3.10"**
- Click **"Next"**

### 3.5 Done

- You'll see: "Web app created successfully"
- Copy the path shown: `/home/tranvinh028/Major_Recommendation`

✅ **Step 3 Complete**

---

## ⚙️ STEP 4: Configure WSGI File (3-5 minutes)

### 4.1 Open WSGI Configuration

- Go back to **Web** tab
- Click on **"tranvinh028.pythonanywhere.com"** web app
- Scroll down to **"WSGI configuration file"**
- You'll see a path like: `/var/www/tranvinh028_pythonanywhere_com_wsgi.py`
- Click the link to edit

### 4.2 Clear Default Content

- Select all (Ctrl+A)
- Delete everything

### 4.3 Paste New WSGI Config

Copy and paste this entire content:

```python
import sys
import os
from pathlib import Path

# PROJECT PATH SETUP
project_home = '/home/tranvinh028/Major_Recommendation'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# VIRTUAL ENVIRONMENT ACTIVATION
activate_this = '/home/tranvinh028/.virtualenvs/major-rec/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# ENVIRONMENT VARIABLES SETUP
os.environ['DEEPSEEK_API_KEY'] = 'sk-880b704d61334b5a9e9ba34a18d0a537'
os.environ['ANTHROPIC_API_KEY'] = 'sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da'
os.environ['CLAUDE_BACKUP_KEY'] = 'sk-52eb797508a111c6f62cd677d23b5feed662f5d94390c86c34e14f3b0ec52176'
os.environ['SECRET_KEY'] = 'major-recommendation-prod-secret-2026'

# IMPORT FLASK APPLICATION
from app import app as application
application.config['ENV'] = 'production'
application.config['DEBUG'] = False
```

### 4.4 Save

- Click **"Save"** button (top-right)
- You should see: "File saved successfully"

✅ **Step 4 Complete**

---

## 🔑 STEP 5: Setup Environment Variables (2 minutes)

### 5.1 Go Back to Web App Settings

- Click on **"tranvinh028.pythonanywhere.com"** in Web tab
- Scroll down to **"Environment variables"** section

### 5.2 Add Environment Variables

Click "Add" for each:

**Variable 1:**

- Name: `DEEPSEEK_API_KEY`
- Value: `sk-880b704d61334b5a9e9ba34a18d0a537`
- Click "Add"

**Variable 2:**

- Name: `ANTHROPIC_API_KEY`
- Value: `sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da`
- Click "Add"

**Variable 3:**

- Name: `SECRET_KEY`
- Value: `major-recommendation-prod-secret-2026`
- Click "Add"

### 5.3 Verify

You should see 3 environment variables listed.

✅ **Step 5 Complete**

---

## 🔄 STEP 6: Verify Models & Reload (2 minutes)

### 6.1 Check Models (Back in Bash Console)

```bash
# Go back to Bash console
cd ~/Major_Recommendation

# Check if models exist
ls -la models/

# Should see:
# - rf_model.pkl
# - ohe.pkl
# - tfidf.pkl
# - majors.json
# - hybrid_config.json
```

### 6.2 If Models Don't Exist - Train

```bash
# Activate venv first
workon major-rec

# Train model (takes 2-5 minutes)
python train_model.py

# Wait for completion
# You'll see: "Model training complete"
```

### 6.3 Reload Web App

- Go to **Web** tab
- Scroll up to top
- Click **"Reload tranvinh028.pythonanywhere.com"** button
- Wait 10-30 seconds for reload

✅ **Step 6 Complete**

---

## 🧪 STEP 7: Test Deployment (5 minutes)

### 7.1 Test Homepage

- Open browser: `https://tranvinh028.pythonanywhere.com/`
- Should see: **"Dashboard tư vấn ngành học"** page
- If you see this, ✅ deployment successful!

### 7.2 Test Health Endpoint

- Open: `https://tranvinh028.pythonanywhere.com/health`
- Should see JSON:

```json
{
  "status": "ok",
  "model_ready": true,
  "error": null
}
```

### 7.3 Test Prediction Form

- Go back to homepage
- Fill the form:
  - Sở thích chính: `Công nghệ`
  - Môn học yêu thích: `Toán`
  - Kỹ năng nổi bật: `Phân tích dữ liệu`
  - Tính cách: `Tỉ mỉ`
  - Môi trường: `Văn phòng`
  - Mục tiêu nghề nghiệp: `Thu nhập cao`
  - Mô tả: `Em yêu thích dữ liệu và phân tích`
  - Định hướng: `Em muốn trở thành Data Scientist`
- Click "Dự đoán"
- Should see: **Top 3 ngành** with scores

### 7.4 Test Chatbot

- Go to: `https://tranvinh028.pythonanywhere.com/chatbot`
- Type: `Xin chào`
- Should get response from Claude
- Type: `Ngành IT phù hợp với tôi không?`
- Should get detailed answer

✅ **Step 7 Complete**

---

## 🐛 STEP 8: Troubleshooting

### ❌ Error: "500 Internal Server Error"

**Solution:**

1. Check error log: Web tab → **Error log** → Scroll to bottom
2. Look for error message
3. Common issues:
   - Models not trained → Run `python train_model.py`
   - Import error → Check `pip list`
   - Path error → Verify `/home/tranvinh028/` is correct

### ❌ Error: "ModuleNotFoundError: No module named 'flask'"

**Solution:**

1. Virtual environment not activated in WSGI
2. Re-check WSGI file has:
   ```python
   activate_this = '/home/tranvinh028/.virtualenvs/major-rec/bin/activate_this.py'
   exec(open(activate_this).read(), {'__file__': activate_this})
   ```
3. Reload web app

### ❌ Error: "No module named 'app'"

**Solution:**

1. Project path is wrong
2. Check WSGI file:
   ```python
   project_home = '/home/tranvinh028/Major_Recommendation'
   sys.path.insert(0, project_home)
   ```
3. Reload web app

### ❌ Chatbot Not Working (Generic Response)

**Solution:**

1. API keys not set or incorrect
2. Check environment variables in Web app settings
3. Reload web app
4. Check error log for API failures

### ✅ View Server Log

```bash
# In Bash console
cd ~/Major_Recommendation
tail -f /var/log/tranvinh028.pythonanywhere.com.server.log
```

---

## 📊 Monitoring & Maintenance

### Check Web App Status

- Dashboard → **Web** tab
- Green button = Running ✅
- Red button = Error ❌

### Update Code from GitHub

```bash
cd ~/Major_Recommendation
git pull origin main
```

Then reload web app

### View Access Logs

- Web tab → Click app → **Access log**

### Monitor Resources

- Web tab → **CPU time usage**
- Shows usage statistics

---

## 🎉 Deployment Complete!

✅ **Your website is now live at:**

```
https://tranvinh028.pythonanywhere.com
```

**Share this URL with:**

- Teachers/Professors
- Friends & Family
- For Demo/Testing

---

## 📚 Quick Reference

| Task           | Steps                                          |
| -------------- | ---------------------------------------------- |
| View Homepage  | https://tranvinh028.pythonanywhere.com/        |
| Access Chatbot | https://tranvinh028.pythonanywhere.com/chatbot |
| Check Status   | https://tranvinh028.pythonanywhere.com/health  |
| Update Code    | `git pull origin main` then Reload             |
| Train Model    | `python train_model.py`                        |
| View Error Log | Web tab → Error log                            |
| Reload App     | Web tab → Reload button                        |

---

## 🆘 Need Help?

1. **Check Error Log** - Most issues visible there
2. **Review WSGI Config** - Path & venv setup critical
3. **Verify API Keys** - Environment variables must be set
4. **Check Models** - Must exist in `/models/` folder
5. **Reload Web App** - After any changes

---

**Good luck! Your AI Major Recommendation System is now live! 🚀**
