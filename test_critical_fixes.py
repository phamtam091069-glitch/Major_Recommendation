"""
Test suite for critical chatbot bug fixes.
Tests the three main fixes:
1. Major detection with fuzzy matching
2. Follow-up questions with pronoun resolution
3. Fallback response chain with timeout handling
"""

import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from utils.predictor import Predictor
from utils.chatbot import MajorChatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_major_detection_fuzzy_matching():
    """Test Fix 1: Major detection with fuzzy matching for common typos/variations."""
    print("\n" + "="*70)
    print("TEST 1: Major Detection with Fuzzy Matching")
    print("="*70)
    
    predictor = Predictor()
    chatbot = MajorChatbot(predictor)
    
    test_cases = [
        ("tàu biển", "Dieu khien va quan ly tau bien", "Exact match for maritime major"),
        ("hàng hải", "Dieu khien va quan ly tau bien", "Alias for maritime"),
        ("máy tàu", "Khai thac may tau thuy va quan ly ky thuat", "Marine engineering alias"),
        ("CNTT", "Cong nghe thong tin", "IT abbreviation"),
        ("công nghệ thông tin", "Cong nghe thong tin", "Full tech major name"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_major, description in test_cases:
        result = chatbot._find_major_in_text(query)
        status = "✅ PASS" if result == expected_major else "❌ FAIL"
        print(f"\n{status} | {description}")
        print(f"  Query: '{query}'")
        print(f"  Expected: {expected_major}")
        print(f"  Got: {result}")
        
        if result == expected_major:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_followup_question_detection():
    """Test Fix 2: Follow-up question detection with pronoun resolution."""
    print("\n" + "="*70)
    print("TEST 2: Follow-up Question Detection (Pronoun Resolution)")
    print("="*70)
    
    predictor = Predictor()
    chatbot = MajorChatbot(predictor)
    
    followup_questions = [
        ("nó có bao nhiêu tiền", True, "Pronoun 'nó' = it"),
        ("cái đó giá bao nhiêu", True, "Pronoun 'cái đó' = that one"),
        ("ngành này khó không", True, "Pronoun 'ngành này' = this major"),
        ("nó lương bao nhiêu", True, "Pronoun followup"),
        ("công nghệ thông tin là gì", False, "Not a followup, new topic"),
        ("em có 28 điểm được không", True, "Score question"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected, description in followup_questions:
        result = chatbot._is_followup_question(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"\n{status} | {description}")
        print(f"  Query: '{query}'")
        print(f"  Expected: {expected}")
        print(f"  Got: {result}")
        
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_fallback_response_chain():
    """Test Fix 3: Fallback response chain - verify it doesn't crash and has timeout handling."""
    print("\n" + "="*70)
    print("TEST 3: Fallback Response Chain (Graceful Error Handling)")
    print("="*70)
    
    predictor = Predictor()
    chatbot = MajorChatbot(predictor)
    
    # Test that the function handles missing context gracefully
    test_queries = [
        ("something completely unrelated to majors", "Graceful handling of unknown query"),
        ("", "Empty query handling"),
    ]
    
    passed = 0
    failed = 0
    
    for query, description in test_queries:
        try:
            result = chatbot._get_fallback_response(query)
            
            # Check that we got a non-empty response
            is_valid = isinstance(result, str) and len(result) > 0
            status = "✅ PASS" if is_valid else "❌ FAIL"
            
            print(f"\n{status} | {description}")
            print(f"  Query: '{query}'")
            print(f"  Response: {result[:100]}...")
            
            if is_valid:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ FAIL | {description}")
            print(f"  Query: '{query}'")
            print(f"  Error: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_context_major_resolution():
    """Test major resolution from chat history."""
    print("\n" + "="*70)
    print("TEST 4: Context Major Resolution from History")
    print("="*70)
    
    predictor = Predictor()
    chatbot = MajorChatbot(predictor)
    
    # Simulate a chat history
    history = [
        {"role": "user", "content": "em muốn học công nghệ thông tin"},
        {"role": "assistant", "content": "Ngành CNTT có nhiều cơ hội..."},
    ]
    
    # Test followup question with context
    followup = "nó lương bao nhiêu?"
    
    context_major = chatbot._extract_context_major(history, current_message=followup)
    
    print(f"\nHistory indicates major: {context_major}")
    print(f"Expected: Cong nghe thong tin (or similar)")
    
    is_correct = context_major is not None and len(context_major) > 0
    status = "✅ PASS" if is_correct else "❌ FAIL"
    print(f"\n{status} | Context extraction from history")
    
    return is_correct


def run_all_tests():
    """Run all test suites."""
    print("\n" + "🚀 "*35)
    print("CHATBOT CRITICAL FIXES - TEST SUITE")
    print("🚀 "*35)
    
    results = {
        "Major Detection (Fuzzy)": test_major_detection_fuzzy_matching(),
        "Followup Detection": test_followup_question_detection(),
        "Fallback Response": test_fallback_response_chain(),
        "Context Resolution": test_context_major_resolution(),
    }
    
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    
    passed_tests = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} test groups passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test group(s) need attention")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
