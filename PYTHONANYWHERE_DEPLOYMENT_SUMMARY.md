# 🎯 PythonAnywhere Deployment - Complete Summary

**Status:** ✅ Ready to Deploy  
**Date:** April 24, 2026  
**Username:** `tranvinh028`  
**Live URL:** `https://tranvinh028.pythonanywhere.com`

---

## 📦 What Has Been Prepared

### 1. ✅ GitHub Repository

- **URL:** https://github.com/phamtam091069-glitch/Major_Recommendation
- **Status:** Code pushed, 290+ files
- **Latest Commit:** Update README.md with 73 majors

### 2. ✅ API Keys Configured

- **Deepseek API:** `sk-880b704d61334b5a9e9ba34a18d0a537`
- **Claude API #1:** `sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da`
- **Claude API #2:** `sk-52eb797508a111c6f62cd677d23b5feed662f5d94390c86c34e14f3b0ec52176`

### 3. ✅ Deployment Configuration Files

- **WSGI Config:** `PYTHONANYWHERE_WSGI_CONFIG.py` (Ready to use)
- **Step-by-Step Guide:** `PYTHONANYWHERE_STEP_BY_STEP.md` (7 main steps)
- **Original Guide:** `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` (Reference)

### 4. ✅ Training Models

- **Status:** Models exist in `models/` folder
- **Files:** rf_model.pkl, ohe.pkl, tfidf.pkl, majors.json
- **Can Train:** `python train_model.py` (if needed)

---

## 🚀 Quick Deployment (Est. 30-40 minutes)

### Timeline

```
1. Clone Repository (2-3 min)
2. Virtual Environment (3-5 min)
3. Create Web App (2 min)
4. Config WSGI (3-5 min)
5. Setup Variables (2 min)
6. Verify Models (2 min)
7. Reload & Test (5 min)
```

---

## 📋 Deployment Checklist

**STEP 1: Clone Repository**

```bash
cd ~
git clone https://github.com/phamtam091069-glitch/Major_Recommendation.git
cd Major_Recommendation
```

- [ ] Repository cloned
- [ ] Files verified (ls -la)

**STEP 2: Virtual Environment**

```bash
mkvirtualenv --python=/usr/bin/python3.10 major-rec
pip install -r requirements.txt
```

- [ ] VirtualEnv created
- [ ] Dependencies installed
- [ ] Flask verified (pip list | grep Flask)

**STEP 3: Web App**

- [ ] Dashboard → Web tab
- [ ] Add new web app
- [ ] Domain: tranvinh028.pythonanywhere.com
- [ ] Manual configuration → Python 3.10

**STEP 4: WSGI Configuration**

- [ ] Web app → WSGI configuration file
- [ ] Clear default content
- [ ] Paste config from PYTHONANYWHERE_WSGI_CONFIG.py
- [ ] Save

**STEP 5: Environment Variables**

- [ ] Web app → Environment variables
- [ ] Add DEEPSEEK_API_KEY
- [ ] Add ANTHROPIC_API_KEY
- [ ] Add SECRET_KEY

**STEP 6: Models & Reload**

- [ ] Check models (ls -la models/)
- [ ] Train if needed (python train_model.py)
- [ ] Reload web app

**STEP 7: Test**

- [ ] Homepage loads
- [ ] Health endpoint works
- [ ] Prediction form works
- [ ] Chatbot responds

---

## 🧪 Testing URLs

| Test         | URL                                            |
| ------------ | ---------------------------------------------- |
| Homepage     | https://tranvinh028.pythonanywhere.com/        |
| Health Check | https://tranvinh028.pythonanywhere.com/health  |
| Chatbot      | https://tranvinh028.pythonanywhere.com/chatbot |

---

## ⚙️ WSGI Configuration Overview

The WSGI file handles:

1. **Project Path Setup** - Adds project to Python path
2. **Virtual Environment** - Activates major-rec venv
3. **Environment Variables** - Sets API keys
4. **Flask Import** - Loads Flask app
5. **Production Config** - Sets ENV=production, DEBUG=False

**Key Paths:**

```
Project: /home/tranvinh028/Major_Recommendation
VirtualEnv: /home/tranvinh028/.virtualenvs/major-rec/bin/activate_this.py
WSGI File: /var/www/tranvinh028_pythonanywhere_com_wsgi.py
```

---

## 🔐 API Keys Setup

### In WSGI File (Embedded)

```python
os.environ['DEEPSEEK_API_KEY'] = 'sk-880b704d61334b5a9e9ba34a18d0a537'
os.environ['ANTHROPIC_API_KEY'] = 'sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da'
```

### In Environment Variables (Backup)

Same keys added in PythonAnywhere Web app settings for redundancy

### Fallback Chain

1. **Claude** (Primary) - Most capable
2. **Deepseek** (Backup) - Free alternative
3. **ChiaSegGPU** (Last resort) - Limited but free

---

## 📊 Features After Deployment

### Prediction Form ✅

- Input: 8 fields (sở thích, kỹ năng, tính cách, etc.)
- Output: Top 3 ngành with scores
- Model: Hybrid (60% ML + 40% criteria)

### Chatbot ✅

- Chat about majors
- Ask about specific majors
- Get recommendations
- Support fallback chain (Claude → Deepseek → Generic)

### Dashboard ✅

- View all 73 majors
- See recommendations
- Give feedback
- Monitor system health

---

## 🐛 Troubleshooting Quick Guide

| Error            | Solution                    |
| ---------------- | --------------------------- |
| 500 Error        | Check error log (Web tab)   |
| ImportError      | Verify venv in WSGI         |
| No module 'app'  | Check project path in WSGI  |
| Chatbot fails    | Check API keys in env vars  |
| Models not found | Run `python train_model.py` |

---

## 📚 Key Files Reference

| File                                 | Purpose                       |
| ------------------------------------ | ----------------------------- |
| `PYTHONANYWHERE_STEP_BY_STEP.md`     | **USE THIS** - Complete guide |
| `PYTHONANYWHERE_WSGI_CONFIG.py`      | Copy to PythonAnywhere        |
| `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` | Reference guide               |
| `app.py`                             | Flask main application        |
| `train_model.py`                     | Model training script         |
| `requirements.txt`                   | Python dependencies           |

---

## 🎯 Next Steps

### Immediate (Now)

1. Read `PYTHONANYWHERE_STEP_BY_STEP.md`
2. Follow 7 steps in order
3. Test each step

### After Deployment (30 mins)

1. Test homepage
2. Test prediction form
3. Test chatbot
4. Verify all endpoints work

### Maintenance (Ongoing)

1. Monitor error logs
2. Update code: `git pull origin main`
3. Reload app if needed
4. Check API usage

---

## 📞 Important Notes

### Security

- ⚠️ API keys are in WSGI file (production setting)
- ⚠️ Don't commit WSGI to GitHub
- ✅ WSGI file only visible on PythonAnywhere server

### Performance

- Free tier: Reasonable for demo/testing
- Paid tier: Better for production
- Models cached in memory

### Uptime

- PythonAnywhere uptime: 99%
- Free tier: May sleep after inactivity (cold start)
- Paid tier: Always-on

---

## ✨ What You'll Have

✅ **Live Website:** https://tranvinh028.pythonanywhere.com  
✅ **Prediction System:** Top 3 majors recommendation  
✅ **AI Chatbot:** Claude-powered chat support  
✅ **Dashboard:** View all 73 majors  
✅ **Feedback System:** Collect user feedback  
✅ **Mobile Responsive:** Works on all devices

---

## 🚀 You're All Set!

All files are prepared and ready. Just follow the step-by-step guide and your system will be live in 30-40 minutes!

**Start with:** `PYTHONANYWHERE_STEP_BY_STEP.md`

---

**Good luck! Your Major Recommendation System is about to go live! 🎉**
