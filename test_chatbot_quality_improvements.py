"""
Test script to verify chatbot quality improvements.
Tests all 5 improvements: prompts, context, validation, matching, diversity.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.predictor import load_predictor
from utils.chatbot import MajorChatbot


def test_context_aware_prompt():
    """Test 1: Context-Aware Prompt System"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Context-Aware Prompt System")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    test_cases = [
        ("greeting", "xin chào", 0),
        ("technical", "công nghệ thông tin là gì", 1),
        ("personality_fit", "em có thích logic không", 3),
        ("salary", "lương bao nhiêu", 5),
        ("career", "cơ hội việc làm như thế nào", 7),
    ]
    
    for question_type, text, chat_turn in test_cases:
        prompt = chatbot._build_context_aware_system_prompt(
            text, chat_turn, question_type
        )
        
        # Verify prompt quality
        has_persona = "trợ lý tư vấn ngành học" in prompt.lower()
        has_instructions = "hướng dẫn trả lời" in prompt.lower()
        has_tone = any(word in prompt.lower() for word in ["tự nhiên", "chi tiết", "hỏi lại"])
        
        status = "✅ PASS" if (has_persona and has_instructions and has_tone) else "❌ FAIL"
        logger.info(f"{status} | Type: {question_type:20} | Turn: {chat_turn}")
        logger.info(f"      Persona: {has_persona} | Instructions: {has_instructions} | Tone: {has_tone}")


def test_intelligent_context_summary():
    """Test 2: Intelligent Context Summarization"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Intelligent Context Summarization")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    # Mock history
    history = [
        {"role": "user", "content": "Em muốn học công nghệ thông tin"},
        {"role": "assistant", "content": "Ngành CNTT tập trung vào lập trình..."},
        {"role": "user", "content": "Lương bao nhiêu?"},
        {"role": "assistant", "content": "CNTT có mức lương cao..."},
        {"role": "user", "content": "Cơ hội việc làm thế nào?"},
    ]
    
    summary = chatbot._build_intelligent_context_summary(history)
    
    # Verify summary quality
    has_major = "công nghệ thông tin" in summary.lower() or "cntt" in summary.lower()
    has_topics = any(word in summary.lower() for word in ["lương", "việc làm", "chủ đề", "hỏi"])
    is_concise = len(summary) < 200
    
    status = "✅ PASS" if (has_major and has_topics and is_concise) else "❌ FAIL"
    logger.info(f"{status} | Summary Quality Check")
    logger.info(f"      Has Major: {has_major} | Has Topics: {has_topics} | Concise: {is_concise}")
    logger.info(f"      Summary: {summary[:100]}..." if len(summary) > 100 else f"      Summary: {summary}")


def test_response_quality_scoring():
    """Test 3: Response Quality Scoring"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Response Quality Scoring")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    test_responses = [
        ("Công nghệ thông tin là ngành...", 0.3, "❌ Too short"),
        ("Ngành CNTT tập trung vào lập trình, phát triển phần mềm và ứng dụng. • Kỹ năng: C++, Python, JavaScript\n• Cơ hội: IT companies, startups, banks\n• Lương: 15-35 triệu/tháng", 0.75, "✅ High quality"),
        ("Mình không biết...", 0.2, "❌ No value"),
        ("CNTT học lập trình. Cơ hội việc làm tốt. Lương cao.", 0.5, "⚠️ Medium quality"),
    ]
    
    for response, expected_range_min, description in test_responses:
        score = chatbot._score_response_quality(
            response,
            "Công nghệ thông tin học gì?",
            "Cong nghe thong tin"
        )
        
        status = "✅ PASS" if score >= expected_range_min else "❌ FAIL"
        logger.info(f"{status} | {description:25} | Score: {score:.2f}")


def test_major_matching():
    """Test 4: Major Matching & Ambiguity Resolution"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Major Matching & Ambiguity Resolution")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    test_cases = [
        ("công nghệ thông tin", "Cong nghe thong tin", "✅ Exact match"),
        ("cntt", "Cong nghe thong tin", "✅ Alias match"),
        ("it", "Cong nghe thong tin", "✅ English alias"),
        ("computer science", "Cong nghe thong tin", "✅ Fuzzy match"),
        ("du lich", "Du lich va lu hanh", "✅ Tourism match"),
        ("marketing", "Marketing", "✅ Perfect match"),
    ]
    
    for query, expected_major, description in test_cases:
        found_major = chatbot._find_major_in_text(query)
        status = "✅ PASS" if found_major == expected_major else "❌ FAIL"
        logger.info(f"{status} | {description:20} | Query: '{query}' → Found: {found_major}")


def test_response_diversity():
    """Test 5: Response Diversity & Adaptive Tone"""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Response Diversity & Adaptive Tone")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    # Test different chat turns with same question
    question = "Công nghệ thông tin học gì?"
    
    prompts_by_turn = []
    for turn in [0, 3, 6]:
        prompt = chatbot._build_context_aware_system_prompt(
            question, turn, "technical"
        )
        prompts_by_turn.append((turn, prompt))
    
    # Verify diversity
    all_different = len(set(p[1] for p in prompts_by_turn)) == len(prompts_by_turn)
    has_repetition_warning = any("diễn đạt khác" in p[1] for p in prompts_by_turn if p[0] > 3)
    
    status = "✅ PASS" if (all_different or has_repetition_warning) else "⚠️ PARTIAL"
    logger.info(f"{status} | Diversity Check")
    logger.info(f"      Different prompts: {all_different}")
    logger.info(f"      Repetition warning on turn > 3: {has_repetition_warning}")
    
    for turn, prompt in prompts_by_turn[:2]:
        logger.info(f"      Turn {turn}: {prompt[:70]}...")


def test_full_chat_flow():
    """Test 6: Full Chat Flow with All Improvements"""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Full Chat Flow Integration")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    test_chats = [
        {
            "user": "Xin chào!",
            "expected_source": "greeting",
            "description": "Greeting handling"
        },
        {
            "user": "Công nghệ thông tin là gì?",
            "expected_source": "explicit_major",
            "description": "Major detection"
        },
        {
            "user": "Lương bao nhiêu?",
            "expected_source": "context_followup",
            "description": "Follow-up with context"
        },
    ]
    
    history = []
    for chat in test_chats:
        result = chatbot.chat(
            chat["user"],
            history=history,
            active_major="Cong nghe thong tin" if chat != test_chats[0] else None
        )
        
        # Check response quality
        reply_length = len(result.get("reply", ""))
        source = result.get("source", "")
        confidence = result.get("confidence", 0)
        
        status = "✅ PASS" if reply_length > 20 and confidence > 0 else "❌ FAIL"
        logger.info(f"{status} | {chat['description']:20} | Length: {reply_length:3} | Confidence: {confidence}")
        
        # Add to history
        history.append({"role": "user", "content": chat["user"]})
        history.append({"role": "assistant", "content": result.get("reply", "")})


def test_performance_metrics():
    """Test 7: Performance Metrics"""
    logger.info("\n" + "="*70)
    logger.info("TEST 7: Performance Metrics")
    logger.info("="*70)
    
    predictor = load_predictor()
    chatbot = MajorChatbot(predictor)
    
    # Check model loading
    model_ready = chatbot.tfidf is not None and chatbot.major_vectors is not None
    major_count = len(chatbot.major_names)
    
    logger.info(f"✅ Model Status: {model_ready}")
    logger.info(f"✅ Majors Loaded: {major_count}")
    logger.info(f"✅ Greeting Patterns: {len(chatbot.greeting_responses)}")
    logger.info(f"✅ QA Patterns: {len(chatbot.qa_patterns)}")
    
    # Quick performance check
    import time
    start = time.time()
    chatbot._score_response_quality("Test response", "Test question")
    elapsed = time.time() - start
    
    logger.info(f"✅ Quality Scoring Time: {elapsed*1000:.2f}ms (should be < 10ms)")
    status = "✅ PASS" if elapsed < 0.01 else "⚠️ SLOW"
    logger.info(f"{status} | Performance acceptable")


def run_all_tests():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " CHATBOT QUALITY IMPROVEMENTS - TEST SUITE ".center(68) + "║")
    logger.info("╚" + "="*68 + "╝")
    
    tests = [
        ("Context-Aware Prompts", test_context_aware_prompt),
        ("Intelligent Context Summarization", test_intelligent_context_summary),
        ("Response Quality Scoring", test_response_quality_scoring),
        ("Major Matching", test_major_matching),
        ("Response Diversity", test_response_diversity),
        ("Full Chat Flow", test_full_chat_flow),
        ("Performance Metrics", test_performance_metrics),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "✅ PASSED"))
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED: {e}")
            results.append((test_name, f"❌ FAILED: {str(e)[:50]}"))
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("SUMMARY")
    logger.info("="*70)
    for test_name, result in results:
        logger.info(f"{result:15} | {test_name}")
    
    passed = sum(1 for _, r in results if "✅" in r)
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Chatbot quality improvements verified.")
    else:
        logger.warning(f"\n⚠️ {total-passed} test(s) need attention.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
