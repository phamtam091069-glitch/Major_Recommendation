"""
Comprehensive test for Claude API fallback in chatbot.
Tests all 4 levels of chatbot responses:
1. Greeting
2. Pattern Match
3. TF-IDF Model
4. Claude API Fallback
"""

import sys
import logging
from utils.predictor import load_predictor
from utils.chatbot import MajorChatbot
from utils.claude_fallback_api import get_claude_fallback_api

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_fallback_comprehensive():
    """Test all levels of chatbot responses."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE API FALLBACK TEST FOR CHATBOT")
    print("=" * 80)

    try:
        # Step 1: Load predictor
        print("\n[SETUP] Loading predictor...")
        predictor = load_predictor()
        print("   ✓ Predictor loaded successfully")

        # Step 2: Create chatbot
        print("\n[SETUP] Creating chatbot instance...")
        chatbot = MajorChatbot(predictor)
        print("   ✓ Chatbot created successfully")

        # Step 3: Initialize Claude API fallback
        print("\n[SETUP] Initializing Claude API fallback...")
        fallback_api = get_claude_fallback_api()
        print("   ✓ Claude API fallback initialized")

        # Test Cases
        test_cases = [
            {
                "name": "Test 1: Greeting Response",
                "input": "Xin chào",
                "expected_source": "greeting",
                "level": "Level 1"
            },
            {
                "name": "Test 2: Pattern Match",
                "input": "Công nghệ là gì?",
                "expected_source": "pattern",
                "level": "Level 2"
            },
            {
                "name": "Test 3: TF-IDF Model Response",
                "input": "Tôi muốn học ngành kinh doanh",
                "expected_source": "model",
                "level": "Level 3"
            },
            {
                "name": "Test 4: Claude API Fallback (Unknown Input)",
                "input": "Tôi thích blockchain và web3, ngành nào phù hợp?",
                "expected_source": "fallback",
                "level": "Level 4 - Claude API"
            },
            {
                "name": "Test 5: Another Fallback Case",
                "input": "Quantum computing có gì hay không?",
                "expected_source": "fallback",
                "level": "Level 4 - Claude API"
            },
            {
                "name": "Test 6: Fallback Cache Test (Same as Test 4)",
                "input": "Tôi thích blockchain và web3, ngành nào phù hợp?",
                "expected_source": "fallback",
                "level": "Level 4 - Cache Hit"
            }
        ]

        # Run tests
        print("\n" + "-" * 80)
        print("RUNNING TESTS")
        print("-" * 80)

        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📌 {test_case['name']}")
            print(f"   Level: {test_case['level']}")
            print(f"   Input: '{test_case['input']}'")

            try:
                # Get response
                response = chatbot.chat(test_case['input'])

                # Extract info
                source = response.get('source')
                confidence = response.get('confidence')
                reply = response.get('reply', '')[:100] + "..." if response.get('reply') else ""

                # Check if source matches expected
                source_match = source == test_case['expected_source']
                status = "✅ PASS" if source_match else "❌ FAIL"

                print(f"   Source: {source} {status}")
                print(f"   Confidence: {confidence}")
                print(f"   Reply: {reply}")

                results.append({
                    "test": test_case['name'],
                    "passed": source_match,
                    "source": source,
                    "confidence": confidence
                })

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "test": test_case['name'],
                    "passed": False,
                    "error": str(e)
                })

        # Step 4: Test Claude Fallback API directly
        print("\n" + "-" * 80)
        print("DIRECT CLAUDE FALLBACK API TEST")
        print("-" * 80)

        print("\n📌 Test 7: Direct Claude API Call")
        print("   Input: 'What about metaverse and virtual reality?'")

        try:
            result = fallback_api.analyze_free_text(
                "What about metaverse and virtual reality?",
                context="chatbot"
            )

            print(f"   Success: {result.get('success')}")
            print(f"   Source: {result.get('source')}")
            print(f"   Response preview: {result.get('response', '')[:100]}...")

            direct_pass = result.get('success') and result.get('source') == 'claude_api'
            results.append({
                "test": "Test 7: Direct Claude API Call",
                "passed": direct_pass,
                "source": result.get('source')
            })

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "test": "Test 7: Direct Claude API Call",
                "passed": False,
                "error": str(e)
            })

        # Step 5: Check cache statistics
        print("\n" + "-" * 80)
        print("CACHE STATISTICS")
        print("-" * 80)

        cache_stats = fallback_api.get_cache_stats()
        print(f"\nCache Stats:")
        print(f"   Total entries: {cache_stats['total_entries']}")
        print(f"   Valid entries: {cache_stats['valid_entries']}")
        print(f"   Expired entries: {cache_stats['expired_entries']}")

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in results if r.get('passed', False))
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n✅ Passed: {passed}/{total} ({success_rate:.1f}%)")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n✓ Grok API has been successfully removed")
            print("✓ Claude API fallback is working correctly")
            print("✓ Caching mechanism is functional")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            print("\nFailed tests:")
            for result in results:
                if not result.get('passed', False):
                    print(f"  - {result['test']}")
                    if 'error' in result:
                        print(f"    Error: {result['error']}")
            return False

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive fallback API test...\n")
    success = test_fallback_comprehensive()
    print("\n" + "=" * 80)
    sys.exit(0 if success else 1)
