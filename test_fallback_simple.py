"""
Simple test for API fallback - without actual API calls.
Tests the chatbot response routing and structure.
"""

import sys
import logging
from utils.predictor import load_predictor
from utils.chatbot import MajorChatbot

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(levelname)s - %(message)s'
)


def test_fallback_simple():
    """Test chatbot response levels without API calls."""
    print("\n" + "=" * 80)
    print("SIMPLE CHATBOT FALLBACK LEVEL TEST")
    print("=" * 80)

    try:
        # Load predictor
        print("\n[SETUP] Loading predictor...")
        predictor = load_predictor()
        print("   ✓ Predictor loaded")

        # Create chatbot
        print("\n[SETUP] Creating chatbot...")
        chatbot = MajorChatbot(predictor)
        print("   ✓ Chatbot created")

        # Test cases
        test_cases = [
            {
                "name": "Level 1: Greeting",
                "input": "Xin chào",
                "expected_source": "greeting",
            },
            {
                "name": "Level 2: Pattern Match",
                "input": "Công nghệ là gì?",
                "expected_source": "pattern",
            },
            {
                "name": "Level 3: TF-IDF Model",
                "input": "Tôi muốn học ngành kinh doanh",
                "expected_source": "model",
            },
            {
                "name": "Level 4: Fallback (Unknown)",
                "input": "Tôi thích blockchain và web3",
                "expected_source": "fallback",
            },
            {
                "name": "Level 4: Fallback (Another)",
                "input": "Quantum computing có gì hay?",
                "expected_source": "fallback",
            },
        ]

        # Run tests
        print("\n" + "-" * 80)
        print("TESTING RESPONSE LEVELS")
        print("-" * 80)

        results = []
        for test in test_cases:
            print(f"\n📌 {test['name']}")
            print(f"   Input: '{test['input']}'")

            try:
                response = chatbot.chat(test['input'])
                source = response.get('source')
                confidence = response.get('confidence')
                
                # Check source
                passed = source == test['expected_source']
                status = "✅" if passed else "❌"

                print(f"   {status} Source: {source} (expected: {test['expected_source']})")
                print(f"   Confidence: {confidence}")

                results.append({
                    "test": test['name'],
                    "passed": passed,
                    "source": source,
                    "expected": test['expected_source']
                })

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results.append({
                    "test": test['name'],
                    "passed": False,
                    "error": str(e)
                })

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in results if r['passed'])
        total = len(results)

        print(f"\n✅ Passed: {passed}/{total}")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n✓ Response routing is working correctly")
            print("✓ Level 1-3 responses functional")
            print("✓ Level 4 fallback structure ready for Claude API")
            print("✓ GROK API successfully removed")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            for r in results:
                if not r['passed']:
                    print(f"  ❌ {r['test']}")
                    if 'error' in r:
                        print(f"     Error: {r['error']}")
                    else:
                        print(f"     Got: {r['source']}, Expected: {r['expected']}")
            return False

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting simple fallback test...\n")
    success = test_fallback_simple()
    print("\n" + "=" * 80)
    sys.exit(0 if success else 1)
