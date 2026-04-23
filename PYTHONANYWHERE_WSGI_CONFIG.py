# ============================================================================
# WSGI Configuration for PythonAnywhere Deployment
# PythonAnywhere Username: tranvinh028
# Domain: tranvinh028.pythonanywhere.com
# ============================================================================

import sys
import os
from pathlib import Path

# ============================================================================
# 1. PROJECT PATH SETUP
# ============================================================================
# Add project directory to Python path
project_home = '/home/tranvinh028/Major_Recommendation'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================================
# 2. VIRTUAL ENVIRONMENT ACTIVATION
# ============================================================================
# Activate the virtual environment
activate_this = '/home/tranvinh028/.virtualenvs/major-rec/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})
else:
    print("WARNING: Virtual environment activation file not found!")

# ============================================================================
# 3. ENVIRONMENT VARIABLES SETUP
# ============================================================================
# These can also be set in PythonAnywhere Web app settings
# But setting here ensures they're available immediately

os.environ['DEEPSEEK_API_KEY'] = os.getenv(
    'DEEPSEEK_API_KEY', 
    'sk-880b704d61334b5a9e9ba34a18d0a537'
)

os.environ['ANTHROPIC_API_KEY'] = os.getenv(
    'ANTHROPIC_API_KEY',
    'sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f10792461038a39b03cabb8f68da'
)

# Backup Claude key (in case primary fails)
os.environ['CLAUDE_BACKUP_KEY'] = os.getenv(
    'CLAUDE_BACKUP_KEY',
    'sk-52eb797508a111c6f62cd677d23b5feed662f5d94390c86c34e14f3b0ec52176'
)

os.environ['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'major-recommendation-prod-secret-2026'
)

# ============================================================================
# 4. LOGGING SETUP
# ============================================================================
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WSGI')
logger.info(f"✓ WSGI Config Loaded - Project: {project_home}")
logger.info(f"✓ Virtual Environment: {activate_this}")
logger.info(f"✓ API Keys Configured: DEEPSEEK, ANTHROPIC")

# ============================================================================
# 5. IMPORT FLASK APPLICATION
# ============================================================================
try:
    from app import app as application
    logger.info("✓ Flask Application Imported Successfully")
except Exception as e:
    logger.error(f"✗ Failed to import Flask app: {e}")
    raise

# ============================================================================
# ADDITIONAL CONFIGURATION
# ============================================================================
# Ensure app configuration for production
application.config['ENV'] = 'production'
application.config['DEBUG'] = False

logger.info("✓ WSGI Configuration Complete - Ready for Production")
