"""
Fallback API handler for handling out-of-dataset user inputs.
This module has been deprecated - GROK API KEY has been removed.
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# ⚠️ GROK API Support Removed - API key no longer supported
# This file is kept for backward compatibility but GROK API is disabled

# Cache configuration
CACHE_TTL_SECONDS = 3600  # 1 hour


class GrokFallbackAPI:
    """⚠️ DEPRECATED: Grok API fallback has been removed."""

    def __init__(self, api_key: str = "", cache_ttl: int = CACHE_TTL_SECONDS):
        """
        Initialize fallback API handler (Grok API removed).
        
        Args:
            api_key: No longer used (Grok API key removed)
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_key = ""  # Grok API key removed
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.warning("⚠️ GrokFallbackAPI initialized but GROK API key removed")

    def _get_cache_key(self, text: str, context: str = "") -> str:
        """Generate cache key from text and context."""
        return f"{text}_{context}".lower()[:100]

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

    def _call_grok_api(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Call Grok API with retry logic.
        
        Args:
            prompt: The prompt to send to Grok
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from Grok API or None if failed
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": GROK_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }

        try:
            logger.info(f"📤 Calling Grok API...")
            response = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                logger.info(f"✓ Grok API response received ({len(content)} chars)")
                return content
            else:
                logger.warning("No choices in Grok API response")
                return None

        except requests.exceptions.Timeout:
            logger.error("⚠ Grok API timeout (30s)")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("⚠ Grok API connection error")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"⚠ Grok API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"⚠ Grok API error: {str(e)}")
            return None

    def analyze_free_text(
        self,
        user_text: str,
        major_profiles: Optional[Dict[str, str]] = None,
        context: str = "chatbot"
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
        cache_key = self._get_cache_key(user_text, context)
        
        # Check cache first
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Build prompt for Grok
        if context == "form":
            prompt = f"""Phân tích thông tin sau của học sinh và gợi ý 3 ngành đại học phù hợp nhất:

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
        else:  # chatbot context
            prompt = f"""Trả lời câu hỏi của học sinh về các ngành đại học và lộ trình học tập.

Câu hỏi/Thông tin: {user_text}

Yêu cầu:
1. Trả lời ngắn gọn, tự nhiên, thân thiện bằng tiếng Việt.
2. Ưu tiên 2-4 câu hoặc 1 đoạn ngắn, bám đúng câu hỏi hiện tại.
3. Không dùng tiêu đề, không đánh số mục, không liệt kê theo dàn ý trừ khi người dùng yêu cầu rõ.
4. Nếu hỏi về ngành cụ thể, chỉ nêu thông tin cần thiết nhất.
5. Có thể đề xuất một bước tiếp theo nếu thật sự phù hợp.

Trả về câu trả lời tự nhiên, không cần JSON."""

        # Call Grok API
        response_text = self._call_grok_api(prompt, max_tokens=600)

        if response_text:
            result = {
                "success": True,
                "source": "grok_api",
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
                        logger.info("✓ Successfully parsed Grok JSON response")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Could not parse Grok response as JSON: {e}")
        else:
            result = {
                "success": False,
                "source": "grok_api",
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
        Get major recommendation based on user profile with Grok fallback.
        
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
_fallback_api_instance: Optional[GrokFallbackAPI] = None


def get_fallback_api() -> GrokFallbackAPI:
    """Get or create global fallback API instance."""
    global _fallback_api_instance
    if _fallback_api_instance is None:
        _fallback_api_instance = GrokFallbackAPI()
    return _fallback_api_instance
