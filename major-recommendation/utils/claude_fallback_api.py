"""
Fallback API handler using Anthropic Claude for handling out-of-dataset user inputs.
Uses Claude Haiku 4.5 for intelligent responses when model confidence is low.
"""

import hashlib
import json
import logging
import os
from typing import Any, Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Use official Anthropic endpoint (or custom if needed)
CLAUDE_API_URL = os.getenv("CLAUDE_API_URL", None)
CLAUDE_MODEL = "claude-3-5-haiku-20241022"

# Cache configuration
CACHE_TTL_SECONDS = 3600  # 1 hour


class ClaudeFallbackAPI:
    """Handler for Anthropic Claude fallback when model confidence is low."""

    def _format_conversation_history(self, history: Optional[List[Dict[str, Any]]], max_messages: int = 20) -> str:
        """Format recent conversation history for prompt context."""
        if not history:
            return ""

        recent_items = []
        for item in history[-max_messages:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "")).strip()
            content = str(item.get("content", "")).strip()
            if role not in {"user", "assistant"} or not content:
                continue
            label = "Người dùng" if role == "user" else "Trợ lý"
            recent_items.append(f"{label}: {content}")

        return "\n".join(recent_items)

    def _build_prompt(
        self,
        user_text: str,
        context: str = "chatbot",
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> str:
        """Build prompt text for Claude."""
        conversation_history = self._format_conversation_history(history)

        if context == "chatbot":
            prompt = """Bạn là chatbot tư vấn ngành học cho sinh viên Việt Nam.
Nhiệm vụ của bạn là trả lời dựa trên ngữ cảnh hội thoại gần nhất và câu hỏi hiện tại của người dùng.

Quy tắc:
- Trả lời bằng tiếng Việt, tự nhiên, thân thiện.
- Ưu tiên 2-4 câu ngắn gọn hoặc 1 đoạn ngắn.
- Không dùng tiêu đề, không đánh số mục, không liệt kê theo dàn ý trừ khi người dùng yêu cầu rõ ràng.
- Nếu người dùng đang hỏi tiếp một ý trước đó, hãy dùng ngữ cảnh hội thoại để hiểu đối tượng/ngành đang được nhắc tới.
- Nếu thiếu ngữ cảnh quan trọng, hỏi lại đúng 1 câu ngắn để làm rõ.
- Không nhắc rằng bạn đang làm theo prompt hay quy tắc nội bộ."""
        else:
            prompt = "Bạn là chuyên gia tư vấn chọn ngành học cho học sinh/sinh viên Việt Nam. Trả lời bằng tiếng Việt."

        context_hints = []
        if active_major:
            context_hints.append(f"Ngành đang được nhắc tới: {active_major}")
        if active_topic:
            context_hints.append(f"Chủ đề hiện tại: {active_topic}")

        if context_hints:
            prompt += "\n\nGợi ý ngữ cảnh nội bộ:\n" + "\n".join(context_hints)

        if conversation_history:
            prompt += f"""

Ngữ cảnh hội thoại gần nhất:
{conversation_history}

Câu hỏi hiện tại của người dùng:
{user_text}
"""
        else:
            prompt += f"""

Câu hỏi hiện tại của người dùng:
{user_text}
"""

        return prompt

    def __init__(self, api_key: str = ANTHROPIC_API_KEY, cache_ttl: int = CACHE_TTL_SECONDS):
        """
        Initialize Claude fallback API handler.
        
        Args:
            api_key: Anthropic API key
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        # Initialize Anthropic client with official endpoint
        if CLAUDE_API_URL:
            self.client = Anthropic(api_key=self.api_key, base_url=CLAUDE_API_URL)
            logger.info(f"✓ ClaudeFallbackAPI initialized with {CLAUDE_MODEL} at {CLAUDE_API_URL}")
        else:
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"✓ ClaudeFallbackAPI initialized with {CLAUDE_MODEL} (official Anthropic endpoint)")

    def _get_cache_key(
        self,
        text: str,
        context: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> str:
        """Generate cache key from text, context và ngữ cảnh hội thoại."""
        history_fingerprint = self._format_conversation_history(history)
        payload = "|".join([
            str(text or "").strip().lower(),
            str(context or "").strip().lower(),
            str(active_major or "").strip().lower(),
            str(active_topic or "").strip().lower(),
            history_fingerprint[-500:].lower(),
        ])
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return digest[:32]

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if "timestamp" not in cache_entry:
            return False
        elapsed = (datetime.now() - datetime.fromisoformat(cache_entry["timestamp"])).total_seconds()
        return elapsed < self.cache_ttl

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

    def _call_claude_api(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Call Anthropic Claude API.
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from Claude API or None if failed
        """
        try:
            logger.info(f"📤 Calling Claude API ({CLAUDE_MODEL})...")
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                timeout=30.0
            )
            
            if message.content and len(message.content) > 0:
                content = message.content[0].text
                logger.info(f"✓ Claude API response received ({len(content)} chars)")
                return content
            else:
                logger.warning("No content in Claude API response")
                return None

        except Exception as e:
            logger.error(f"⚠ Claude API error: {str(e)}", exc_info=True)
            return None

    def analyze_free_text(
        self,
        user_text: str,
        major_profiles: Optional[Dict[str, str]] = None,
        context: str = "chatbot",
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze free-form user text and provide major recommendations.
        
        Args:
            user_text: User's input text (can be out-of-dataset)
            major_profiles: Dictionary of available majors
            context: Context of the request ('chatbot' or 'form')
            
        Returns:
            Dict with analysis result and confidence
        """
        cache_key = self._get_cache_key(
            user_text,
            context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
        )

        # Check cache first
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Build prompt for Claude
        prompt = self._build_prompt(
            user_text,
            context=context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
        )

        # Call Claude API
        response_text = self._call_claude_api(prompt, max_tokens=600)

        if response_text:
            result = {
                "success": True,
                "source": "claude_api",
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
                        logger.info("✓ Successfully parsed Claude JSON response")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Could not parse Claude response as JSON: {e}")
        else:
            result = {
                "success": False,
                "source": "claude_api",
                "response": None,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }

        # Save to cache
        self._save_cache(cache_key, result)
        return result

    def get_major_recommendation(
        self,
        user_profile: Dict[str, str],
        available_majors: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Get major recommendation based on user profile with Claude fallback.
        
        Args:
            user_profile: User input data
            available_majors: List of available majors
            
        Returns:
            Dictionary with recommendation
        """
        # Build profile text from user input
        profile_text = self._build_profile_text(user_profile)
        return self.analyze_free_text(profile_text, context="form")

    def _build_profile_text(self, user_profile: Dict[str, str]) -> str:
        """Build human-readable profile text from user input."""
        parts = []
        
        field_labels = {
            "so_thich_chinh": "Sở thích chính",
            "mon_hoc_yeu_thich": "Môn học yêu thích",
            "ky_nang_noi_bat": "Kỹ năng nổi bật",
            "tinh_cach": "Tính cách",
            "moi_truong_lam_viec_mong_muon": "Môi trường làm việc mong muốn",
            "muc_tieu_nghe_nghiep": "Mục tiêu nghề nghiệp",
            "mo_ta_ban_than": "Mô tả bản thân",
            "dinh_huong_tuong_lai": "Định hướng tương lai"
        }
        
        for field, label in field_labels.items():
            value = user_profile.get(field, "").strip()
            if value:
                parts.append(f"- {label}: {value}")
        
        return "\n".join(parts) if parts else "Không có thông tin"

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
_claude_fallback_api_instance: Optional[ClaudeFallbackAPI] = None


def get_claude_fallback_api() -> ClaudeFallbackAPI:
    """Get or create global Claude fallback API instance."""
    global _claude_fallback_api_instance
    if _claude_fallback_api_instance is None:
        _claude_fallback_api_instance = ClaudeFallbackAPI()
    return _claude_fallback_api_instance
