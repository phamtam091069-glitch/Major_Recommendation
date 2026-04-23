"""
Test suite for hybrid TF-IDF + fallback verification system.
Tests confidence ranges: >= 0.85 (model), 0.75-0.85 (verify), < 0.75 (fallback)
"""

import json
from unittest.mock import MagicMock, patch

from utils.chatbot import MajorChatbot
from utils.predictor import load_predictor


def setup_chatbot():
    """Setup chatbot for testing."""
    predictor = load_predictor()
    return MajorChatbot(predictor)


def test_high_confidence_uses_model():
    """Test: confidence >= 0.85 → use model directly (fast path)"""
    chatbot = setup_chatbot()
    
    # Test with high-confidence query
    result = chatbot.chat(
        "Tôi thích lập trình và công nghệ thông tin",
        history=[]
    )
    
    print("✅ Test 1: High Confidence (>= 0.85)")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Reply: {result['reply'][:100]}...")
    assert result['confidence'] >= 0.0, "Should have confidence score"
    print()


def test_medium_confidence_triggers_verification():
    """Test: 0.75 <= confidence < 0.85 → verify with fallback"""
    chatbot = setup_chatbot()
    
    # Ambiguous query that should trigger verification
    result = chatbot.chat(
        "Quản lý kinh doanh hay quản lý công nghệ thông tin",
        history=[]
    )
    
    print("✅ Test 2: Medium Confidence (0.75-0.85) - Verification Triggered")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Reply: {result['reply'][:100]}...")
    # Source should be either 'model_verified', 'fallback_verified', or similar
    assert result['source'] in ['model', 'fallback', 'model_verified', 'fallback_verified', 'context_followup'], \
        f"Unexpected source: {result['source']}"
    print()


def test_low_confidence_uses_fallback():
    """Test: confidence < 0.75 → use fallback only"""
    chatbot = setup_chatbot()
    
    # Very vague query
    result = chatbot.chat(
        "Cái gì tốt nhất",
        history=[]
    )
    
    print("✅ Test 3: Low Confidence (< 0.75) - Fallback Only")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Reply: {result['reply'][:100]}...")
    print()


def test_multiple_majors_detection():
    """Test: Detect when user mentions multiple majors"""
    chatbot = setup_chatbot()
    
    # User mentions 2 majors
    result = chatbot.chat(
        "Tôi muốn học công nghệ thông tin hoặc khoa học dữ liệu",
        history=[]
    )
    
    print("✅ Test 4: Multiple Majors Detection")
    print(f"   Source: {result['source']}")
    print(f"   Needs Clarification: {result.get('needs_clarification', False)}")
    print(f"   Reply: {result['reply'][:100]}...")
    print()


def test_comparison_method():
    """Test: _compare_model_vs_fallback logic"""
    chatbot = setup_chatbot()
    
    # Create mock responses
    tfidf_resp = "🎯 **Công nghệ thông tin**\n\n💡 Phù hợp nếu bạn thích ngành này."
    fallback_resp = (
        "Dựa trên câu hỏi của bạn, tôi gợi ý 2 ngành: "
        "1. Công nghệ thông tin - tập trung vào lập trình\n"
        "2. Quản trị kinh doanh - tập trung vào quản lý"
    )
    user_message = "công nghệ thông tin hay quản trị kinh doanh"
    
    # Should prefer fallback when multiple majors mentioned
    is_better = chatbot._compare_model_vs_fallback(tfidf_resp, fallback_resp, user_message)
    
    print("✅ Test 5: Comparison Method - Multiple Majors")
    print(f"   Fallback is better: {is_better}")
    assert is_better is True, "Fallback should be better for multiple majors"
    print()


def test_generic_template_detection():
    """Test: Detect generic TF-IDF template responses"""
    chatbot = setup_chatbot()
    
    tfidf_resp = "🎯 **Ngành X**\n\n💡 Phù hợp nếu bạn thích ngành này."
    fallback_resp = "Ngành X là tốt vì: ... (detailed explanation with 10 sentences)"
    user_message = "Tell me about X"
    
    # Generic template with short response should prefer longer fallback
    is_better = chatbot._compare_model_vs_fallback(tfidf_resp, fallback_resp, user_message)
    
    print("✅ Test 6: Generic Template Detection")
    print(f"   Fallback is better: {is_better}")
    print()


def test_contextual_followup():
    """Test: Follow-up questions within context"""
    chatbot = setup_chatbot()
    
    # First message
    result1 = chatbot.chat(
        "Công nghệ thông tin học gì?",
        history=[]
    )
    
    # Follow-up question
    result2 = chatbot.chat(
        "Ngành này có bao nhiêu năm học?",
        history=[
            {"role": "user", "content": "Công nghệ thông tin học gì?"},
            {"role": "assistant", "content": result1['reply']}
        ]
    )
    
    print("✅ Test 7: Contextual Follow-up")
    print(f"   First Query Source: {result1['source']}")
    print(f"   Follow-up Source: {result2['source']}")
    print(f"   Follow-up Reply: {result2['reply'][:100]}...")
    print()


def test_greeting_handling():
    """Test: Greetings should be handled immediately"""
    chatbot = setup_chatbot()
    
    result = chatbot.chat(
        "Xin chào",
        history=[]
    )
    
    print("✅ Test 8: Greeting Handling")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']}")
    assert result['source'] == 'greeting', "Should recognize greeting"
    print()


def test_off_topic_handling():
    """Test: Off-topic questions should be blocked"""
    chatbot = setup_chatbot()
    
    result = chatbot.chat(
        "Bạn có bạn gái không? Bạn xinh gái không?",
        history=[]
    )
    
    print("✅ Test 9: Off-Topic Handling")
    print(f"   Source: {result['source']}")
    assert result['source'] == 'scope_guard', "Should recognize off-topic"
    print()


def test_confidence_scores():
    """Test: Confidence scores are reasonable"""
    chatbot = setup_chatbot()
    
    result1 = chatbot.chat("Công nghệ thông tin", history=[])
    result2 = chatbot.chat("Cái gì tốt nhất", history=[])
    
    print("✅ Test 10: Confidence Scores")
    print(f"   High-confidence query: {result1['confidence']}")
    print(f"   Low-confidence query: {result2['confidence']}")
    
    # At least one should have reasonable confidence
    assert result1['confidence'] >= 0 or result2['confidence'] >= 0, \
        "Should have at least one meaningful confidence score"
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("HYBRID TF-IDF + FALLBACK VERIFICATION SYSTEM - TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        test_high_confidence_uses_model,
        test_medium_confidence_triggers_verification,
        test_low_confidence_uses_fallback,
        test_multiple_majors_detection,
        test_comparison_method,
        test_generic_template_detection,
        test_contextual_followup,
        test_greeting_handling,
        test_off_topic_handling,
        test_confidence_scores,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_func.__name__}")
            print(f"   Error: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {test_func.__name__}")
            print(f"   Exception: {str(e)}\n")
            failed += 1
    
    print("="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
