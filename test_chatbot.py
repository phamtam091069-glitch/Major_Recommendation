"""
Quick test script for chatbot functionality.
"""

import sys
from utils.predictor import load_predictor
from utils.chatbot import MajorChatbot

def test_chatbot():
    """Test chatbot with sample messages."""
    print("=" * 60)
    print("TESTING CHATBOT FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Load predictor
        print("\n1. Loading predictor...")
        predictor = load_predictor()
        print("   ✓ Predictor loaded successfully")
        
        # Create chatbot
        print("\n2. Creating chatbot instance...")
        chatbot = MajorChatbot(predictor)
        print("   ✓ Chatbot created successfully")
        
        # Test messages
        test_messages = [
            "Xin chào",
            "Công nghệ là gì?",
            "Em muốn học ngành kinh doanh",
            "Random question about majors",
        ]
        
        print("\n3. Testing chatbot responses:")
        print("-" * 60)
        
        for i, msg in enumerate(test_messages, 1):
            print(f"\n   Message {i}: '{msg}'")
            response = chatbot.chat(msg)
            print(f"   Source: {response.get('source')}")
            print(f"   Confidence: {response.get('confidence')}")
            print(f"   Reply: {response.get('reply')[:100]}...")
        
        print("\n" + "=" * 60)
        print("✓ CHATBOT TEST PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chatbot()
    sys.exit(0 if success else 1)
