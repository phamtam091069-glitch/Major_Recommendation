"""
WSGI Configuration for PythonAnywhere Deployment
This file should be placed in the WSGI configuration area of PythonAnywhere
or can be used as reference for manual WSGI config
"""
import sys
import os
from pathlib import Path

# ====== PROJECT SETUP ======
# IMPORTANT: Change 'username' to your PythonAnywhere username
PYTHONANYWHERE_USERNAME = "username"  # ← CHANGE THIS!
PROJECT_NAME = "major-recommendation"
PROJECT_HOME = f"/home/{PYTHONANYWHERE_USERNAME}/{PROJECT_NAME}"

# Add project to Python path
if project_home not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# ====== VIRTUAL ENVIRONMENT ======
# Activate virtual environment
VENV_PATH = f"/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/major-rec/bin/activate_this.py"
try:
    exec(open(VENV_PATH).read(), {'__file__': VENV_PATH})
except FileNotFoundError:
    print(f"⚠️ Virtual environment not found at {VENV_PATH}")
    print("Make sure you created it with: mkvirtualenv --python=/usr/bin/python3.10 major-rec")

# ====== ENVIRONMENT VARIABLES ======
# These should be set in PythonAnywhere Web app settings
# But we read them here as fallback
os.environ.setdefault('ANTHROPIC_API_KEY', '')
os.environ.setdefault('OPENAI_API_KEY', '')
os.environ.setdefault('SECRET_KEY', 'pythonanywhere-dev-key')
os.environ.setdefault('FLASK_ENV', 'production')

# ====== FLASK APP ======
try:
    from app import app as application
    print("✓ Flask app imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print(f"Make sure app.py is in {PROJECT_HOME}")
    # Fallback error app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"Error: Could not import app. Check logs.", 500

# ====== OPTIONAL: Setup Logging ======
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler(f'/home/{PYTHONANYWHERE_USERNAME}/logs/wsgi.log')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("WSGI application started")
