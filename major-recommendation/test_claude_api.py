"""
Test script to verify Claude API is working correctly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (from project root)
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Verify API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY", "")
print(f"✓ API Key loaded: {api_key[:20]}...{api_key[-10:]}")

if not api_key:
    print("✗ ERROR: ANTHROPIC_API_KEY not found in .env")
    exit(1)

# Now test the chatbot
print("\n" + "=" * 60)
print("TESTING CHATBOT WITH CLAUDE API")
print("=" * 60)

from utils.predictor import load_predictor
from utils.chatbot import MajorChatbot

try:
    print("\n1. Loading predictor...")
    predictor = load_predictor()
    print("   ✓ Predictor loaded successfully")
    
    print("\n2. Creating chatbot instance...")
    chatbot = MajorChatbot(predictor)
    print("   ✓ Chatbot created successfully")
    
    print("\n3. Testing chatbot responses with Claude API:")
    print("-" * 60)
    
    test_messages = [
        "Xin chào",
        "tôi rất mê máy tính thì nên chọn ngành nào",
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n   Message {i}: '{msg}'")
        response = chatbot.chat(msg)
        print(f"   Source: {response.get('source')}")
        print(f"   Confidence: {response.get('confidence')}")
        print(f"   Reply: {response.get('reply')[:150]}...")
    
    print("\n" + "=" * 60)
    print("✓ CHATBOT TEST PASSED")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
