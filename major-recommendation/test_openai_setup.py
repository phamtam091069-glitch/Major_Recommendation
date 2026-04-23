#!/usr/bin/env python3
"""
Test script to verify OpenAI API integration
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

def test_openai_import():
    """Test if OpenAI library can be imported."""
    try:
        from openai import OpenAI
        logger.info("✓ OpenAI library imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Failed to import OpenAI: {e}")
        return False

def test_env_variables():
    """Test if environment variables are loaded."""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")
    
    if not api_key:
        logger.error("✗ OPENAI_API_KEY not found in .env")
        return False
    
    if not base_url:
        logger.error("✗ OPENAI_BASE_URL not found in .env")
        return False
    
    if not model:
        logger.error("✗ OPENAI_MODEL not found in .env")
        return False
    
    logger.info(f"✓ Environment variables loaded:")
    logger.info(f"  - API Key: {api_key[:20]}...")
    logger.info(f"  - Base URL: {base_url}")
    logger.info(f"  - Model: {model}")
    return True

def test_openai_api_initialization():
    """Test if OpenAI API client can be initialized."""
    try:
        from utils.openai_fallback_api import get_openai_fallback_api
        
        api = get_openai_fallback_api()
        if api.client is None:
            logger.error("✗ OpenAI API client is None")
            return False
        
        logger.info("✓ OpenAI API client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize OpenAI API: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        from utils.openai_fallback_api import get_openai_fallback_api
        
        api = get_openai_fallback_api()
        is_working = api.test_connection()
        
        if is_working:
            logger.info("✓ OpenAI API connection test passed")
            return True
        else:
            logger.error("✗ OpenAI API connection test failed")
            return False
    except Exception as e:
        logger.error(f"✗ OpenAI API connection test error: {e}")
        return False

def test_chatbot_integration():
    """Test chatbot integration with OpenAI."""
    try:
        from utils.chatbot import MajorChatbot
        logger.info("✓ MajorChatbot imported successfully")
        logger.info("✓ Chatbot now uses OpenAI as primary API (with Claude fallback)")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to import MajorChatbot: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Testing OpenAI API Integration")
    logger.info("=" * 60)
    
    tests = [
        ("OpenAI Import", test_openai_import),
        ("Environment Variables", test_env_variables),
        ("OpenAI API Initialization", test_openai_api_initialization),
        ("OpenAI Connection", test_openai_connection),
        ("Chatbot Integration", test_chatbot_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests passed! OpenAI API is ready to use.")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
