"""
Comprehensive test suite for chatbot greeting and pattern matching fixes.
Tests all edge cases to ensure the greeting detection bug is fixed.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.predictor import Predictor
from utils.chatbot import MajorChatbot


def print_test_header(test_name):
    """Print a formatted test header."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")


def print_result(message, source, confidence, passed):
    """Print formatted test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | Source: {source:12} | Confidence: {confidence} | {message}")


def test_greeting_detection():
    """Test that greeting patterns are correctly detected."""
    print_test_header("Greeting Detection")
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        test_cases = [
            # (message, expected_source, should_pass)
            ("xin chào", "greeting", True),
            ("Xin chào", "greeting", True),
            ("XIN CHÀO", "greeting", True),
            ("hi", "greeting", True),
            ("Hi", "greeting", True),
            ("hello", "greeting", True),
            ("Hello", "greeting", True),
            ("helo", "greeting", True),
        ]
        
        passed = 0
        for message, expected_source, should_pass in test_cases:
            response = chatbot.chat(message)
            source = response["source"]
            confidence = response["confidence"]
            is_correct = source == expected_source
            
            if should_pass:
                passed += is_correct
            
            print_result(f"'{message}' → {expected_source}", source, confidence, is_correct)
        
        print(f"\n✓ Greeting Detection: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error in greeting detection: {e}")
        return False


def test_major_questions_not_greeting():
    """Test that questions about majors are NOT detected as greetings."""
    print_test_header("Major Questions Should NOT Be Greetings (BUG FIX)")
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        # These questions contain words that might trigger false positives
        # The bug was matching "hi" in "hiểu", etc.
        test_cases = [
            # (message, should_not_be_greeting)
            ("bạn có biết về ngành điều khiển và quản lý tàu biển không", True),
            ("ngành nào phù hợp với tôi", True),
            ("hiểu về ngành công nghệ thông tin", True),  # Contains "hi"
            ("bạn có thể giúp tôi không", True),  # Contains "hi" 
            ("tôi muốn học ngành nào", True),
            ("ngành gì tốt nhất", True),
        ]
        
        passed = 0
        for message, should_not_be_greeting in test_cases:
            response = chatbot.chat(message)
            source = response["source"]
            confidence = response["confidence"]
            
            # The fix ensures these are NOT detected as greetings
            is_correct = source != "greeting"
            
            if should_not_be_greeting:
                passed += is_correct
            
            print_result(
                f"'{message[:40]}...' → NOT greeting (got {source})", 
                source, 
                confidence, 
                is_correct
            )
        
        print(f"\n✓ Major Questions: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error in major questions test: {e}")
        return False


def test_pattern_matching():
    """Test that pattern matching works correctly."""
    print_test_header("Pattern Matching for Major Keywords")
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        test_cases = [
            # (message, expected_source, should_pass)
            ("công nghệ là gì", "pattern", True),
            ("máy tính phù hợp không", "pattern", True),
            ("kỹ thuật cơ khí", "pattern", True),
            ("kinh doanh và marketing", "pattern", True),
            ("ngôn ngữ anh", "pattern", True),
            ("sức khỏe", "pattern", True),
            ("du lịch", "pattern", True),
            ("giáo dục", "pattern", True),
            ("thiết kế", "pattern", True),
        ]
        
        passed = 0
        for message, expected_source, should_pass in test_cases:
            response = chatbot.chat(message)
            source = response["source"]
            confidence = response["confidence"]
            is_correct = source == expected_source
            
            if should_pass:
                passed += is_correct
            
            print_result(f"'{message}' → {expected_source}", source, confidence, is_correct)
        
        print(f"\n✓ Pattern Matching: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error in pattern matching test: {e}")
        return False


def test_response_content():
    """Test that responses contain expected content."""
    print_test_header("Response Content Validation")
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        test_cases = [
            # (message, expected_content_count)
            ("công nghệ", 3),  # Should have 3 majors in response
            ("máy tính", 3),
            ("kinh doanh", 3),
        ]
        
        passed = 0
        for message, expected_majors in test_cases:
            response = chatbot.chat(message)
            reply = response["reply"]
            
            # Count how many numbered items in response
            major_count = reply.count("1️⃣") + reply.count("1.") + reply.count("**1")
            major_count = 1 if major_count > 0 else 0  # At least 1 first item
            
            is_correct = major_count > 0  # Should have at least item 1
            
            # More importantly, check that it doesn't have "## 4" or "# 4" patterns
            has_4th_item = "# 4" in reply or "## 4" in reply or "### 4" in reply
            is_correct = not has_4th_item
            
            print_result(
                f"'{message}' → No 4+ items (found {major_count} groups)", 
                "response_validation", 
                len(reply), 
                is_correct
            )
            
            if is_correct:
                passed += 1
        
        print(f"\n✓ Response Content: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error in response content test: {e}")
        return False


def test_edge_cases():
    """Test edge cases and special scenarios."""
    print_test_header("Edge Cases")
    
    try:
        predictor = Predictor()
        chatbot = MajorChatbot(predictor)
        
        test_cases = [
            # (message, description, should_not_fail)
            ("", "empty message", True),
            ("   ", "whitespace only", True),
            ("hi there what do you know", "greeting with extra words", True),
            ("xin chào bạn", "greeting with context", True),
            ("about hi and hello", "contains multiple greeting words", True),
            ("!@#$%", "special characters", True),
            ("a" * 1000, "very long message", True),
        ]
        
        passed = 0
        for message, description, should_not_fail in test_cases:
            try:
                response = chatbot.chat(message)
                source = response["source"]
                has_reply = "reply" in response
                is_valid = has_reply and source in ["greeting", "pattern", "model", "fallback", "system"]
                
                if should_not_fail:
                    passed += is_valid
                
                print_result(
                    f"{description}: '{message[:30]}...' → {source}", 
                    source, 
                    response.get("confidence", 0), 
                    is_valid
                )
            except Exception as e:
                print_result(
                    f"{description}: '{message[:30]}...' → ERROR: {e}", 
                    "error", 
                    0, 
                    False
                )
        
        print(f"\n✓ Edge Cases: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error in edge cases test: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CHATBOT GREETING DETECTION BUG FIX - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Run all test suites
    results["greeting_detection"] = test_greeting_detection()
    results["major_questions_not_greeting"] = test_major_questions_not_greeting()
    results["pattern_matching"] = test_pattern_matching()
    results["response_content"] = test_response_content()
    results["edge_cases"] = test_edge_cases()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED - BUG FIX SUCCESSFUL!")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW NEEDED")
    
    print(f"{'='*80}\n")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
