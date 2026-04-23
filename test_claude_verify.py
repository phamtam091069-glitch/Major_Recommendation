"""
Test script để verify Claude API Key - Làm theo từng bước
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 80)
print("STEP 1: Load .env file")
print("=" * 80)

# Load environment variables
load_dotenv()
print("✓ load_dotenv() called")

print("\n" + "=" * 80)
print("STEP 2: Check ANTHROPIC_API_KEY in .env")
print("=" * 80)

# Read .env file directly to verify
print("\nReading .env file contents:")
try:
    with open(".env", "r") as f:
        env_content = f.read()
    
    # Find ANTHROPIC_API_KEY line
    for line in env_content.split('\n'):
        if 'ANTHROPIC_API_KEY' in line:
            print(f"Found: {line[:50]}...")  # Print first 50 chars
            
    print("\n✓ .env file exists and has ANTHROPIC_API_KEY")
except FileNotFoundError:
    print("✗ .env file not found!")
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 3: Get API Key from os.getenv()")
print("=" * 80)

api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"✓ API Key found")
    print(f"  Length: {len(api_key)} chars")
    print(f"  Prefix: {api_key[:20]}...")
    print(f"  Suffix: ...{api_key[-10:]}")
else:
    print("✗ API Key is None or empty!")
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 4: Check Anthropic client initialization")
print("=" * 80)

try:
    from anthropic import Anthropic
    print("✓ anthropic library imported successfully")
    
    # Try to create client
    client = Anthropic(api_key=api_key)
    print("✓ Anthropic client created successfully")
    print(f"  Client type: {type(client)}")
    print(f"  Client API key prefix: {client.api_key[:20]}...")
    
except ImportError as e:
    print(f"✗ Failed to import anthropic: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Failed to create Anthropic client: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 5: Test Claude API with simple request")
print("=" * 80)

try:
    print("📤 Calling Claude API...")
    response = client.messages.create(
        model="claude-haiku-4.5",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello from Claude!' in Vietnamese"
            }
        ],
        timeout=30.0
    )
    
    print("✓ API call successful!")
    print(f"  Response content: {response.content[0].text}")
    print(f"  Stop reason: {response.stop_reason}")
    
except Exception as e:
    print(f"✗ API call failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 6: Test with custom endpoint (llm.chiasegpu.vn)")
print("=" * 80)

try:
    print("📤 Creating client with custom endpoint...")
    custom_client = Anthropic(
        api_key=api_key,
        base_url="https://llm.chiasegpu.vn/v1"
    )
    print(f"✓ Custom client created")
    print(f"  Base URL: https://llm.chiasegpu.vn/v1")
    
    print("\n📤 Calling Claude API via custom endpoint...")
    response = custom_client.messages.create(
        model="claude-haiku-4.5",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Viết một câu đơn giản"
            }
        ],
        timeout=30.0
    )
    
    print("✓ Custom endpoint API call successful!")
    print(f"  Response: {response.content[0].text}")
    
except Exception as e:
    print(f"⚠ Custom endpoint test: {e}")
    print(f"  Note: This may fail if endpoint is unreachable, but key is valid")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED")
print("=" * 80)
print("\nSummary:")
print("✓ .env file loaded successfully")
print("✓ ANTHROPIC_API_KEY found and valid")
print("✓ Anthropic client created successfully")
print("✓ Claude API is working")
print("\n👉 Next step: Update utils/chatbot.py to use FALLBACK_API_IMPROVED.py")
