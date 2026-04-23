"""
Quick test script to verify Claude API endpoint works with chatbot
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.chatbot import MajorChatbot
from utils.predictor import load_predictor


def test_chatbot_api():
    """Test chatbot with various messages"""
    print("\n" + "="*70)
    print("🧪 CHATBOT API TEST")
    print("="*70)
    
    try:
        # Load predictor and create chatbot
        print("\n📦 Loading predictor...")
        predictor = load_predictor()
        chatbot = MajorChatbot(predictor)
        print("✅ Predictor loaded successfully")
        
        # Test messages
        test_cases = [
            ("xin chào", "Greeting"),
            ("công nghệ", "Pattern match"),
            ("tôi thích lập trình và AI", "Fallback (low confidence)"),
        ]
        
        print("\n" + "-"*70)
        print("🧪 Testing Chatbot Responses")
        print("-"*70)
        
        for i, (message, test_type) in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {test_type}")
            print(f"Input: {message}")
            
            response = chatbot.chat(message)
            
            # Check response structure
            required_fields = ["reply", "source", "confidence"]
            missing = [f for f in required_fields if f not in response]
            
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False
            
            print(f"✅ PASS")
            print(f"  - Source: {response.get('source')}")
            print(f"  - Confidence: {response.get('confidence')}")
            print(f"  - Reply: {response.get('reply')[:100]}...")
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chatbot_api()
    sys.exit(0 if success else 1)
