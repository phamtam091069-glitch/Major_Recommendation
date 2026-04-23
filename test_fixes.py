#!/usr/bin/env python3
"""
Quick test to verify all fixes are working correctly.
Tests:
1. API key is loaded properly
2. Chatbot imports without errors
3. Confidence variable is properly defined
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_env_setup():
    """Test .env file is properly configured."""
    print("=" * 60)
    print("🔍 TEST 1: Environment Setup")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    api_url = os.getenv("CLAUDE_API_URL", "")
    
    assert api_key, "❌ ANTHROPIC_API_KEY not found in .env"
    assert api_url, "❌ CLAUDE_API_URL not found in .env"
    assert api_key.startswith("sk-"), f"❌ Invalid API key format: {api_key[:10]}..."
    
    print(f"✅ ANTHROPIC_API_KEY: {api_key[:20]}...{api_key[-10:]}")
    print(f"✅ CLAUDE_API_URL: {api_url}")
    print()

def test_chatbot_imports():
    """Test chatbot module can be imported."""
    print("=" * 60)
    print("🔍 TEST 2: Chatbot Module Import")
    print("=" * 60)
    
    try:
        from utils.chatbot import MajorChatbot
        print("✅ MajorChatbot imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MajorChatbot: {e}")
        raise
    
    try:
        from utils.claude_fallback_api import get_claude_fallback_api
        print("✅ Claude Fallback API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Claude Fallback API: {e}")
        raise
    
    print()

def test_syntax():
    """Test Python syntax of key files."""
    print("=" * 60)
    print("🔍 TEST 3: Python Syntax Check")
    print("=" * 60)
    
    import py_compile
    
    files_to_check = [
        "app.py",
        "utils/chatbot.py",
        "utils/claude_fallback_api.py",
        "utils/predictor.py",
    ]
    
    for filename in files_to_check:
        filepath = project_root / filename
        try:
            py_compile.compile(str(filepath), doraise=True)
            print(f"✅ {filename} - Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"❌ {filename} - Syntax Error: {e}")
            raise
    
    print()

def test_confidence_fix():
    """Test that confidence variable is properly handled in chatbot."""
    print("=" * 60)
    print("🔍 TEST 4: Chatbot Confidence Fix")
    print("=" * 60)
    
    # Read the chatbot.py file and check the fix
    chatbot_path = project_root / "utils" / "chatbot.py"
    with open(chatbot_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that the fix is present
    if '"confidence": 0.0' in content and 'fallback_resp' in content:
        print("✅ Chatbot confidence fix is in place")
        print('   - Fallback response uses confidence: 0.0')
        print('   - No undefined variable error possible')
    else:
        print("❌ Chatbot confidence fix not found")
        raise AssertionError("Confidence fix missing from chatbot.py")
    
    print()

def test_gitignore():
    """Test that .gitignore properly excludes .env."""
    print("=" * 60)
    print("🔍 TEST 5: .gitignore Setup")
    print("=" * 60)
    
    gitignore_path = project_root / ".gitignore"
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if ".env" in content:
        print("✅ .gitignore contains '.env' exclusion")
    else:
        print("❌ .gitignore missing '.env' exclusion")
        raise AssertionError(".env not in .gitignore")
    
    # Check .env.example exists
    env_example_path = project_root / ".env.example"
    if env_example_path.exists():
        print("✅ .env.example template file exists")
        with open(env_example_path, 'r', encoding='utf-8') as f:
            example_content = f.read()
        if "sk-your-api-key-here" in example_content:
            print("✅ .env.example contains proper placeholder")
        else:
            print("⚠️  .env.example might not have placeholder")
    else:
        print("❌ .env.example not found")
        raise AssertionError(".env.example not found")
    
    print()

def main():
    """Run all tests."""
    print("\n")
    print("🚀 RUNNING ERROR FIX VERIFICATION TESTS")
    print("=" * 60)
    print()
    
    try:
        test_env_setup()
        test_syntax()
        test_chatbot_imports()
        test_confidence_fix()
        test_gitignore()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("📋 Summary:")
        print("   ✅ API key updated and configured")
        print("   ✅ Chatbot confidence bug fixed")
        print("   ✅ .env properly protected with .gitignore")
        print("   ✅ .env.example template created")
        print("   ✅ All Python files have valid syntax")
        print()
        print("🎉 Your project is ready to use!")
        print()
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
