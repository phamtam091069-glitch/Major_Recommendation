"""
Test script to verify fallback API response format is correct.
This tests the fixes made to the fallback API response mapping.
"""

import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.chatbot import MajorChatbot
from utils.claude_fallback_api import get_claude_fallback_api
from utils.predictor import load_predictor


def test_claude_fallback_response_format():
    """Test that Claude fallback API returns correct response format."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Claude Fallback API Response Format")
    print("="*70)
    
    try:
        fallback_api = get_claude_fallback_api()
        
        # Test with a simple question
        test_text = "Tôi thích lập trình"
        print(f"\n📝 Input: {test_text}")
        
        result = fallback_api.analyze_free_text(test_text, context="chatbot")
        
        print(f"\n✓ Response received from Claude API")
        print(f"  - Success: {result.get('success')}")
        print(f"  - Source: {result.get('source')}")
        print(f"  - Has 'response' field: {'response' in result}")
        
        # Check response structure
        if result.get("success"):
            response_text = result.get("response", "")
            if response_text:
                print(f"  - Response length: {len(response_text)} chars")
                print(f"  - Response preview: {response_text[:100]}...")
                return True
            else:
                print(f"  ❌ ERROR: Empty response text")
                return False
        else:
            print(f"  ❌ ERROR: success=False")
            print(f"  Full result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in Claude API test: {e}", exc_info=True)
        return False


def test_chatbot_fallback_mapping():
    """Test that chatbot correctly maps fallback response to 'reply' field."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Chatbot Fallback Response Mapping")
    print("="*70)
    
    try:
        predictor = load_predictor()
        chatbot = MajorChatbot(predictor)
        
        # Use a question with low TF-IDF confidence to trigger fallback
        test_message = "Hãy giải thích về các ngành học mới"
        print(f"\n📝 Input message: {test_message}")
        
        response = chatbot.chat(test_message)
        
        print(f"\n✓ Response received from chatbot")
        print(f"  - Has 'reply' field: {'reply' in response}")
        print(f"  - Source: {response.get('source')}")
        print(f"  - Confidence: {response.get('confidence')}")
        
        if "reply" in response:
            reply_text = response.get("reply", "")
            if reply_text:
                print(f"  - Reply length: {len(reply_text)} chars")
                print(f"  - Reply preview: {reply_text[:100]}...")
                print(f"\n✅ PASS: Response format is correct!")
                return True
            else:
                print(f"  ❌ ERROR: Empty reply text")
                return False
        else:
            print(f"  ❌ ERROR: Missing 'reply' field")
            print(f"  Response keys: {response.keys()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in chatbot test: {e}", exc_info=True)
        return False


def test_response_structure():
    """Test that response structure matches expected format."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Response Structure Validation")
    print("="*70)
    
    try:
        predictor = load_predictor()
        chatbot = MajorChatbot(predictor)
        
        test_messages = [
            "xin chào",  # Greeting
            "công nghệ",  # Pattern match
            "lập trình là gì",  # TF-IDF match or fallback
        ]
        
        all_passed = True
        for i, message in enumerate(test_messages, 1):
            print(f"\n  Test {i}: {message}")
            response = chatbot.chat(message)
            
            # Check required fields
            required_fields = ["reply", "source", "confidence"]
            missing_fields = [f for f in required_fields if f not in response]
            
            if missing_fields:
                print(f"    ❌ Missing fields: {missing_fields}")
                all_passed = False
            else:
                print(f"    ✓ All required fields present")
                print(f"      Source: {response.get('source')}")
                print(f"      Confidence: {response.get('confidence')}")
        
        if all_passed:
            print(f"\n✅ PASS: All response structures are valid!")
        return all_passed
            
    except Exception as e:
        logger.error(f"❌ Error in structure test: {e}", exc_info=True)
        return False


def main():
    """Run all tests."""
    print("\n" + "🔍 "*15)
    print("API FALLBACK CHATBOT - FIX VERIFICATION TESTS")
    print("🔍 "*15)
    
    results = []
    
    # Test 1: Claude API response format
    test1_passed = test_claude_fallback_response_format()
    results.append(("Claude API Response Format", test1_passed))
    
    # Test 2: Chatbot fallback mapping
    test2_passed = test_chatbot_fallback_mapping()
    results.append(("Chatbot Fallback Mapping", test2_passed))
    
    # Test 3: Response structure validation
    test3_passed = test_response_structure()
    results.append(("Response Structure", test3_passed))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Fallback API fixes are working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
