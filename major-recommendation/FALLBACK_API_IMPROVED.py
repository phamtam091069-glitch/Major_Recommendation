"""
⚠️ DEPRECATED: Grok API support has been removed.
This file is kept for historical reference only.

Previously: Improved Fallback API Handler with Claude + Grok
Now: Claude API only
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Try importing Claude client
try:
    from anthropic import Anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False

import requests

load_dotenv()
logger = logging.getLogger(__name__)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://llm.chiasegpu.vn/v1")
CLAUDE_MODEL = "claude-haiku-4.5"

# ⚠️ GROK API REMOVED - No longer supported

# Cache & Retry Settings
CACHE_TTL_SECONDS = 3600
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


class ImprovedFallbackAPI:
    """
    Improved fallback API handler with:
    - Claude API support
    - Retry logic with exponential backoff
    - Better error handling
    - Response validation
    - Comprehensive logging

    ⚠️ NOTE: Grok API support has been removed
    """

    def __init__(self):
        self.api_key_claude = ANTHROPIC_API_KEY
        self._cache: Dict[str, Dict[str, Any]] = {}

        if HAS_CLAUDE and self.api_key_claude:
            # Use custom endpoint if provided
            if ANTHROPIC_API_URL:
                self.client_claude = Anthropic(api_key=self.api_key_claude, base_url=ANTHROPIC_API_URL)
                logger.info(f"✓ Claude client initialized with custom endpoint: {ANTHROPIC_API_URL}")
            else:
                self.client_claude = Anthropic(api_key=self.api_key_claude)
                logger.info("✓ Claude client initialized with official endpoint")
        else:
            self.client_claude = None
            logger.warning("⚠ Claude client not available")

    def _get_cache_key(self, text: str, context: str = "") -> str:
        """Generate cache key from text and context."""
        return f"{text}_{context}".lower()[:100]

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if "timestamp" not in cache_entry:
            return False
        elapsed = (datetime.now() - datetime.fromisoformat(cache_entry["timestamp"])).total_seconds()
        return elapsed < CACHE_TTL_SECONDS

    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check and retrieve from cache if valid."""
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
            logger.info(f"✓ Cache hit for: {cache_key}")
            return self._cache[cache_key]["result"]
        return None

    def _save_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Save result to cache."""
        self._cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"✓ Cached result for: {cache_key}")

    def _call_claude_api_with_retry(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Call Claude API with retry logic."""
        if not self.client_claude:
            logger.warning("⚠ Claude client not available")
            return None

        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"📤 Calling Claude API (attempt {attempt + 1}/{MAX_RETRIES})...")
                message = self.client_claude.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=30.0
                )

                if message.content and len(message.content) > 0:
                    content = message.content[0].text
                    logger.info(f"✓ Claude API response received ({len(content)} chars)")
                    return content
                else:
                    logger.warning("No content in Claude API response")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"⚠ Claude API timeout (attempt {attempt + 1})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                continue
            except Exception as e:
                logger.error(f"⚠ Claude API error (attempt {attempt + 1}): {str(e)}", exc_info=True)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                continue

        logger.error("✗ Claude API failed after all retries")
        return None

    def analyze_free_text(self, user_text: str, context: str = "chatbot") -> Dict[str, Any]:
        """Analyze free-form user text with Claude API."""
        cache_key = self._get_cache_key(user_text, context)

        # Check cache first
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Build prompt based on context
        if context == "form":
            prompt = self._build_form_prompt(user_text)
        else:
            prompt = self._build_chatbot_prompt(user_text)

        # Try Claude
        if self.client_claude:
            response_text = self._call_claude_api_with_retry(prompt)
            if response_text:
                result = self._build_success_response(response_text, "claude", context)
                self._save_cache(cache_key, result)
                return result

        # Final fallback
        result = self._build_error_response(context)
        self._save_cache(cache_key, result)
        return result

    def _build_form_prompt(self, user_text: str) -> str:
        """Build prompt for form analysis."""
        return f"""Phân tích thông tin sau của học sinh và gợi ý 3 ngành đại học phù hợp nhất:

{user_text}

Yêu cầu:
1. Phân tích các điểm mạnh, sở thích, kỹ năng từ text
2. Gợi ý 3 ngành phù hợp (ưu tiên cao → thấp)
3. Giải thích tại sao phù hợp
4. Đánh giá độ phù hợp (0-100%)

Trả về JSON với format:
{{
  "strengths": ["...", "..."],
  "top_3_majors": [
    {{"major": "...", "reason": "...", "fit_score": 85}},
    {{"major": "...", "reason": "...", "fit_score": 75}},
    {{"major": "...", "reason": "...", "fit_score": 65}}
  ],
  "overall_recommendation": "..."
}}"""

    def _build_chatbot_prompt(self, user_text: str) -> str:
        """Build prompt for chatbot context."""
        return f"""Trả lời câu hỏi của học sinh về các ngành đại học và lộ trình học tập:

Câu hỏi/Thông tin: {user_text}

Yêu cầu:
1. Trả lời một cách thân thiện, khuyến khích (Tiếng Việt)
2. Nếu hỏi về ngành cụ thể, giải thích chi tiết
3. Nếu hỏi chung chung, gợi ý cách xác định ngành phù hợp
4. Đề xuất bước tiếp theo (như điền form chi tiết)

Trả về câu trả lời tự nhiên, không cần JSON."""

    def _build_success_response(self, response_text: str, source: str, context: str) -> Dict[str, Any]:
        """Build success response."""
        result = {
            "success": True,
            "source": source,
            "response": response_text,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

        # Try to parse as JSON if context is 'form'
        if context == "form":
            try:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed = json.loads(json_str)
                    result["parsed_data"] = parsed
                    logger.info("✓ Successfully parsed JSON response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Could not parse response as JSON: {e}")

        return result

    def _build_error_response(self, context: str) -> Dict[str, Any]:
        """Build error response when API fails."""
        return {
            "success": False,
            "source": "none",
            "response": None,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "error": "Claude API failed"
        }

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()
        logger.info("✓ Cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        valid_count = sum(1 for entry in self._cache.values() if self._is_cache_valid(entry))
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_count,
            "expired_entries": len(self._cache) - valid_count
        }


# Global instance
_improved_fallback_api_instance: Optional[ImprovedFallbackAPI] = None


def get_improved_fallback_api() -> ImprovedFallbackAPI:
    """Get or create global improved fallback API instance."""
    global _improved_fallback_api_instance
    if _improved_fallback_api_instance is None:
        _improved_fallback_api_instance = ImprovedFallbackAPI()
    return _improved_fallback_api_instance
