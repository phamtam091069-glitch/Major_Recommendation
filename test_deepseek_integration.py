"""
Test script to verify DeepSeek API integration and check for conflicts
between different API fallback implementations.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all API modules can be imported without conflicts."""
    logger.info("=" * 60)
    logger.info("TEST 1: Checking API Module Imports")
    logger.info("=" * 60)
    
    try:
        from utils.deepseek_fallback_api import get_deepseek_fallback_api, DeepseekFallbackAPI
        logger.info("✅ DeepSeek API module imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import DeepSeek API: {e}")
        return False
    
    try:
        from utils.openai_fallback_api import get_openai_fallback_api, OpenAIFallbackAPI
        logger.info("✅ OpenAI API module imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import OpenAI API: {e}")
        return False
    
    try:
        from utils.claude_fallback_api import get_claude_fallback_api, ClaudeFallbackAPI
        logger.info("✅ Claude API module imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import Claude API: {e}")
        return False
    
    logger.info("✅ All API modules imported without conflicts\n")
    return True


def test_api_instantiation():
    """Test that all API instances can be created without conflicts."""
    logger.info("=" * 60)
    logger.info("TEST 2: API Instantiation")
    logger.info("=" * 60)
    
    try:
        from utils.deepseek_fallback_api import get_deepseek_fallback_api
        deepseek_api = get_deepseek_fallback_api()
        logger.info(f"✅ DeepSeek API instantiated: {deepseek_api.__class__.__name__}")
        logger.info(f"   - Base URL: {deepseek_api.base_url}")
        logger.info(f"   - Model: {deepseek_api.model}")
        logger.info(f"   - Client initialized: {deepseek_api.client is not None}")
    except Exception as e:
        logger.error(f"❌ Failed to instantiate DeepSeek API: {e}")
        return False
    
    try:
        from utils.openai_fallback_api import get_openai_fallback_api
        openai_api = get_openai_fallback_api()
        logger.info(f"✅ OpenAI API instantiated: {openai_api.__class__.__name__}")
        logger.info(f"   - Base URL: {openai_api.base_url}")
        logger.info(f"   - Model: {openai_api.model}")
        logger.info(f"   - Client initialized: {openai_api.client is not None}")
    except Exception as e:
        logger.error(f"❌ Failed to instantiate OpenAI API: {e}")
        return False
    
    try:
        from utils.claude_fallback_api import get_claude_fallback_api
        claude_api = get_claude_fallback_api()
        logger.info(f"✅ Claude API instantiated: {claude_api.__class__.__name__}")
        logger.info(f"   - Client initialized: {claude_api.client is not None}")
    except Exception as e:
        logger.error(f"❌ Failed to instantiate Claude API: {e}")
        return False
    
    logger.info("✅ All APIs instantiated successfully\n")
    return True


def test_fallback_chain_order():
    """Test that the fallback chain is in correct order (DeepSeek first)."""
    logger.info("=" * 60)
    logger.info("TEST 3: Fallback Chain Order Verification")
    logger.info("=" * 60)
    
    try:
        # Import the app to check the fallback chain
        import app as app_module
        
        # Check the _normalize_payload_via_fallback function with UTF-8 encoding
        with open(Path(__file__).parent / "app.py", "r", encoding="utf-8", errors="ignore") as f:
            source_code = f.read()
        
        # Find the fallback chain definition
        if 'fallback_chain = [' in source_code:
            logger.info("✅ Found fallback_chain definition in app.py")
            
            # Extract the chain order
            if '("deepseek", get_deepseek_fallback_api),' in source_code:
                deepseek_pos = source_code.find('("deepseek", get_deepseek_fallback_api),')
                openai_pos = source_code.find('("openai", get_openai_fallback_api),')
                claude_pos = source_code.find('("claude", get_claude_fallback_api),')
                
                if deepseek_pos < openai_pos < claude_pos:
                    logger.info("✅ Fallback chain order is CORRECT:")
                    logger.info("   1. DeepSeek (FIRST - HIGHEST PRIORITY)")
                    logger.info("   2. OpenAI (Second)")
                    logger.info("   3. Claude (Third)")
                    return True
                else:
                    logger.error("❌ Fallback chain order is INCORRECT")
                    logger.error(f"   Positions: DeepSeek={deepseek_pos}, OpenAI={openai_pos}, Claude={claude_pos}")
                    return False
            else:
                logger.error("❌ DeepSeek not found in fallback chain")
                return False
        else:
            logger.error("❌ Fallback chain definition not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking fallback chain: {e}")
        return False


def test_api_methods():
    """Test that all APIs have the required methods."""
    logger.info("=" * 60)
    logger.info("TEST 4: API Methods Verification")
    logger.info("=" * 60)
    
    required_methods = [
        'analyze_free_text',
        '_build_prompt',
        '_format_conversation_history',
    ]
    
    # Optional methods (not all APIs may have these)
    optional_methods = {
        'test_connection',  # Claude doesn't have this
    }
    
    apis_to_test = [
        ('DeepSeek', 'utils.deepseek_fallback_api', 'get_deepseek_fallback_api'),
        ('OpenAI', 'utils.openai_fallback_api', 'get_openai_fallback_api'),
        ('Claude', 'utils.claude_fallback_api', 'get_claude_fallback_api'),
    ]
    
    all_passed = True
    
    for api_name, module_name, factory_name in apis_to_test:
        try:
            module = __import__(module_name, fromlist=[factory_name])
            factory = getattr(module, factory_name)
            api_instance = factory()
            
            # Check required methods
            missing_methods = []
            for method in required_methods:
                if not hasattr(api_instance, method):
                    missing_methods.append(method)
            
            if missing_methods:
                logger.error(f"❌ {api_name} API missing required methods: {missing_methods}")
                all_passed = False
            else:
                logger.info(f"✅ {api_name} API has all required methods")
                
                # Check optional methods
                missing_optional = []
                for method in optional_methods:
                    if not hasattr(api_instance, method):
                        missing_optional.append(method)
                
                if missing_optional and api_name == 'Claude':
                    logger.warning(f"⚠️ {api_name} API missing optional methods: {missing_optional} (pre-existing)")
                elif missing_optional:
                    logger.warning(f"⚠️ {api_name} API missing optional methods: {missing_optional}")
                
        except Exception as e:
            logger.error(f"❌ Error testing {api_name} API methods: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("✅ All APIs have all required methods\n")
    else:
        logger.info("❌ Some APIs are missing required methods\n")
    
    return all_passed


def test_env_configuration():
    """Test that environment variables are correctly configured."""
    logger.info("=" * 60)
    logger.info("TEST 5: Environment Configuration Check")
    logger.info("=" * 60)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check DeepSeek config
    deepseek_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
    deepseek_url = os.getenv('DEEPSEEK_BASE_URL', '').strip()
    deepseek_model = os.getenv('DEEPSEEK_MODEL', '').strip()
    
    if deepseek_key and deepseek_url and deepseek_model:
        logger.info("✅ DeepSeek configuration found:")
        logger.info(f"   - API Key: {'*' * 10}...{deepseek_key[-10:]}")
        logger.info(f"   - Base URL: {deepseek_url}")
        logger.info(f"   - Model: {deepseek_model}")
    else:
        logger.warning("⚠️ DeepSeek configuration incomplete")
        logger.warning(f"   - API Key present: {bool(deepseek_key)}")
        logger.warning(f"   - Base URL present: {bool(deepseek_url)}")
        logger.warning(f"   - Model present: {bool(deepseek_model)}")
    
    # Check OpenAI config
    openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    openai_url = os.getenv('OPENAI_BASE_URL', '').strip()
    
    if openai_key and openai_url:
        logger.info("✅ OpenAI configuration found:")
        logger.info(f"   - API Key: {'*' * 10}...{openai_key[-10:] if len(openai_key) > 10 else '***'}")
        logger.info(f"   - Base URL: {openai_url}")
    else:
        logger.warning("⚠️ OpenAI configuration incomplete")
    
    # Check Claude config
    claude_key = os.getenv('ANTHROPIC_API_KEY', '').strip()
    
    if claude_key:
        logger.info("✅ Claude configuration found:")
        logger.info(f"   - API Key: {'*' * 10}...{claude_key[-10:] if len(claude_key) > 10 else '***'}")
    else:
        logger.warning("⚠️ Claude configuration incomplete")
    
    logger.info("")
    return bool(deepseek_key and deepseek_url and deepseek_model)


def test_app_imports():
    """Test that app.py can import without conflicts."""
    logger.info("=" * 60)
    logger.info("TEST 6: App.py Import Verification")
    logger.info("=" * 60)
    
    try:
        import app
        logger.info("✅ app.py imported successfully")
        
        # Check that DeepSeek is imported
        if hasattr(app, 'get_deepseek_fallback_api'):
            logger.info("✅ get_deepseek_fallback_api is available in app module")
        else:
            logger.warning("⚠️ get_deepseek_fallback_api not directly accessible in app module")
        
        logger.info("")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to import app.py: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("")
        return False


def run_all_tests():
    """Run all tests and report results."""
    logger.info("\n" + "=" * 60)
    logger.info("DEEPSEEK API INTEGRATION TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("API Instantiation", test_api_instantiation),
        ("Fallback Chain Order", test_fallback_chain_order),
        ("API Methods", test_api_methods),
        ("Environment Configuration", test_env_configuration),
        ("App.py Import", test_app_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            logger.error(traceback.format_exc())
            results.append((test_name, False))
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! DeepSeek API integration is complete and conflict-free.")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
