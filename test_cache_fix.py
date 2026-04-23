#!/usr/bin/env python3
"""
Test script to verify the cache key fix in _get_fallback_response()
This test ensures that different questions get different responses (not cached incorrectly)
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cache_fix():
    """Test that different questions get different responses from Deepseek fallback API"""
    print("\n" + "="*70)
    print("🧪 TEST: Cache Key Fix - Different Questions Should Get Different Responses")
    print("="*70 + "\n")
    
    try:
        from utils.deepseek_fallback_api import get_deepseek_fallback_api
        
        api = get_deepseek_fallback_api()
        
        # Test 1: Question about IT
        print("📝 Question 1: 'Công nghệ thông tin là gì?'")
        result1 = api.analyze_free_text("Công nghệ thông tin là gì?", context="chatbot")
        response1 = result1.get("response", "").strip()[:100] if result1.get("success") else "FAILED"
        print(f"✓ Response (first 100 chars): {response1}")
        print(f"  Success: {result1.get('success')}")
        
        # Test 2: Question about Tourism
        print("\n📝 Question 2: 'Du lịch là ngành gì?'")
        result2 = api.analyze_free_text("Du lịch là ngành gì?", context="chatbot")
        response2 = result2.get("response", "").strip()[:100] if result2.get("success") else "FAILED"
        print(f"✓ Response (first 100 chars): {response2}")
        print(f"  Success: {result2.get('success')}")
        
        # Test 3: Question about Health
        print("\n📝 Question 3: 'Y dược là gì?'")
        result3 = api.analyze_free_text("Y dược là gì?", context="chatbot")
        response3 = result3.get("response", "").strip()[:100] if result3.get("success") else "FAILED"
        print(f"✓ Response (first 100 chars): {response3}")
        print(f"  Success: {result3.get('success')}")
        
        # Verify responses are different
        print("\n" + "="*70)
        print("🔍 VERIFICATION:")
        print("="*70)
        
        if response1 and response2 and response3:
            all_different = (response1 != response2) and (response2 != response3) and (response1 != response3)
            if all_different:
                print("✅ PASS: All three responses are DIFFERENT (cache fix works!)")
                return True
            else:
                print("❌ FAIL: Some responses are THE SAME (cache issue still exists)")
                print(f"   Response 1 == Response 2: {response1 == response2}")
                print(f"   Response 2 == Response 3: {response2 == response3}")
                print(f"   Response 1 == Response 3: {response1 == response3}")
                return False
        else:
            print("⚠️  WARNING: Some responses are empty or failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cache_fix()
    print("\n" + "="*70)
    if success:
        print("✅ TEST PASSED - Cache fix is working correctly!")
    else:
        print("❌ TEST FAILED - Please check the implementation")
    print("="*70 + "\n")
    sys.exit(0 if success else 1)
