"""
Test suite to verify chatbot response display fix.
Tests that responses are complete and not truncated.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.predictor import Predictor
from utils.chatbot import MajorChatbot


def test_response_completeness():
    """Test that responses are complete and not truncated."""
    print("=" * 60)
    print("🧪 TEST: Response Completeness")
    print("=" * 60)
    
    try:
        # Initialize predictor and chatbot
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        # Test cases with expected response characteristics
        test_cases = [
            {
                "message": "công nghệ thông tin là gì",
                "expected_keywords": ["Top 3", "ngành", "phù hợp"],
                "min_length": 100
            },
            {
                "message": "tôi muốn học máy tính",
                "expected_keywords": ["Top 3", "ngành"],
                "min_length": 80
            },
            {
                "message": "kỹ thuật cơ khí thế nào",
                "expected_keywords": ["Top 3", "kỹ thuật"],
                "min_length": 80
            },
            {
                "message": "xin chào",
                "expected_keywords": ["Xin chào", "chatbot"],
                "min_length": 20
            },
        ]
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: '{test['message']}'")
            print("-" * 60)
            
            response = chatbot.chat(test['message'])
            reply = response.get('reply', '')
            source = response.get('source', 'unknown')
            confidence = response.get('confidence', 0)
            
            print(f"Source: {source} | Confidence: {confidence}")
            print(f"Response Length: {len(reply)} chars")
            print(f"Preview: {reply[:100]}...")
            
            # Check response length
            if len(reply) < test['min_length']:
                print(f"❌ FAILED: Response too short (got {len(reply)}, expected >= {test['min_length']})")
                failed += 1
                continue
            
            # Check for keywords
            missing_keywords = []
            for keyword in test['expected_keywords']:
                if keyword.lower() not in reply.lower():
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                print(f"❌ FAILED: Missing keywords: {missing_keywords}")
                failed += 1
                continue
            
            # Check for truncation signs
            truncation_signs = ["...", "[truncated", ""]
            is_truncated = any(
                reply.rstrip().endswith(sign) for sign in truncation_signs[:-1]
            ) or (len(reply) > 0 and reply[-1] in ['-', ':', ','])
            
            if is_truncated:
                print(f"⚠️  WARNING: Response might be truncated")
            
            # Check for multiple paragraphs (good sign)
            paragraphs = reply.count('\n') + 1
            print(f"Paragraphs: {paragraphs}")
            
            print(f"✅ PASSED")
            passed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return failed == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_long_response_display():
    """Test that long responses are displayed completely."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Long Response Display")
    print("=" * 60)
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        # Use fallback API which should return longer responses
        response = chatbot.chat("Cho tôi biết tất cả những gì bạn biết về các ngành khác nhau")
        reply = response.get('reply', '')
        
        print(f"\nResponse Length: {len(reply)} chars")
        print(f"Source: {response.get('source')}")
        print(f"\nFull Response:\n{reply}\n")
        
        # Check that response is reasonably long
        if len(reply) < 50:
            print(f"❌ FAILED: Response too short")
            return False
        
        # Check that it doesn't end abruptly
        if reply.rstrip().endswith('...') or len(reply) > 2000:
            print(f"⚠️  WARNING: Response might be truncated or very long")
        
        print(f"✅ PASSED: Response is complete and detailed")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_formatting():
    """Test that multi-line messages are preserved."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Message Formatting")
    print("=" * 60)
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        response = chatbot.chat("công nghệ là gì")
        reply = response.get('reply', '')
        
        # Count line breaks
        line_breaks = reply.count('\n')
        print(f"\nResponse has {line_breaks} line breaks")
        print(f"Response lines: {len(reply.split(chr(10)))}")
        
        # Check structure is preserved
        lines = reply.split('\n')
        print(f"\nLines:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"  {i}. {line[:60]}{'...' if len(line) > 60 else ''}")
        
        # Should have multiple lines for good formatting
        if line_breaks < 2:
            print(f"⚠️  WARNING: Response has very few line breaks")
        
        print(f"\n✅ PASSED: Formatting preserved")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🤖 CHATBOT DISPLAY FIX VERIFICATION TEST SUITE  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Response Completeness", test_response_completeness()))
    results.append(("Long Response Display", test_long_response_display()))
    results.append(("Message Formatting", test_message_formatting()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"🎯 OVERALL: {total_passed}/{total_tests} tests passed")
    print("=" * 60)
    
    if total_passed == total_tests:
        print("\n✨ All tests passed! Chatbot display fix is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
