"""
ChiaSeGPU LLM Fallback API Integration
API Base: https://llm.chiasegpu.vn/v1
Model: claude-haiku-4.5
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Configuration
CHIASEGPU_API_KEY = os.getenv("CHIASEGPU_API_KEY", "sk-bc59637dd09f8c0f0a11ab46b22e70e5a053f107924610838a39b03cabb8f68da")
CHIASEGPU_BASE_URL = os.getenv("CHIASEGPU_BASE_URL", "https://llm.chiasegpu.vn/v1")
CHIASEGPU_MODEL = os.getenv("CHIASEGPU_MODEL", "claude-haiku-4.5")
REQUEST_TIMEOUT = 10


class ChiaSeGPUFallbackAPI:
    """ChiaSeGPU LLM API wrapper for chatbot fallback."""

    def __init__(self):
        self.api_key = CHIASEGPU_API_KEY
        self.base_url = CHIASEGPU_BASE_URL
        self.model = CHIASEGPU_MODEL
        self.timeout = REQUEST_TIMEOUT

    def _build_messages(
        self,
        user_prompt: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, str]]:
        """Build message list with history context."""
        messages = []
        
        # Add history if provided
        if history and isinstance(history, list):
            for item in history[-5:]:  # Last 5 messages for context
                if isinstance(item, dict) and "role" in item and "content" in item:
                    role = str(item["role"]).strip()
                    content = str(item["content"]).strip()
                    if role in {"user", "assistant"} and content:
                        messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def analyze_free_text(
        self,
        text: str,
        context: str = "chatbot",
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze Vietnamese free text using ChiaSeGPU API.
        
        Args:
            text: User input text
            context: Context type (chatbot, form, etc.)
            history: Chat history for context
            active_major: Currently active major
            active_topic: Currently active topic
            
        Returns:
            Dict with success flag and response
        """
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed")
            return {
                "success": False,
                "response": "",
                "error": "Missing requests library",
            }

        try:
            # Build system prompt based on context
            if context == "form":
                system_prompt = (
                    "Bạn là bộ chuẩn hóa dữ liệu form tư vấn ngành học. "
                    "Nhiệm vụ: map các giá trị không chuẩn về đúng nhãn hợp lệ. "
                    "Chỉ trả về JSON object hợp lệ, không thêm giải thích."
                )
            else:  # chatbot
                system_prompt = (
                    "Bạn là chatbot tư vấn ngành học đại học tại Việt Nam. "
                    "Trả lời bằng tiếng Việt, ngắn gọn và hữu ích. "
                    "Tập trung vào tư vấn ngành học dựa trên sở thích, kỹ năng và định hướng. "
                )
                
                if active_major:
                    system_prompt += f"Ngành đang thảo luận: {active_major}. "
                if active_topic:
                    system_prompt += f"Chủ đề: {active_topic}. "

            messages = self._build_messages(text, history)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "system": system_prompt,
                "max_tokens": 500,
                "temperature": 0.7,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            logger.info(f"📤 Calling ChiaSeGPU API... (timeout={self.timeout}s)")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                logger.warning(f"❌ ChiaSeGPU API error: {response.status_code} - {response.text[:200]}")
                return {
                    "success": False,
                    "response": "",
                    "error": f"API returned {response.status_code}",
                }

            data = response.json()
            
            # Extract response text
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                response_text = message.get("content", "").strip()
                
                if response_text:
                    logger.info(f"✅ ChiaSeGPU API success ({len(response_text)} chars)")
                    return {
                        "success": True,
                        "response": response_text,
                        "source": "chiasegpu",
                        "model": self.model,
                    }
                else:
                    logger.warning("❌ ChiaSeGPU returned empty response")
                    return {
                        "success": False,
                        "response": "",
                        "error": "Empty response from API",
                    }
            else:
                logger.warning(f"❌ Unexpected ChiaSeGPU response structure: {data}")
                return {
                    "success": False,
                    "response": "",
                    "error": "Invalid response structure",
                }

        except requests.exceptions.Timeout:
            logger.warning(f"⏱️  ChiaSeGPU API timeout (>{self.timeout}s)")
            return {
                "success": False,
                "response": "",
                "error": "Request timeout",
            }
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"🔌 ChiaSeGPU connection error: {e}")
            return {
                "success": False,
                "response": "",
                "error": "Connection error",
            }
        except Exception as e:
            logger.error(f"💥 ChiaSeGPU API error: {e}")
            return {
                "success": False,
                "response": "",
                "error": str(e),
            }


# Singleton instance
_chiasegpu_api_instance: Optional[ChiaSeGPUFallbackAPI] = None


def get_chiasegpu_fallback_api() -> ChiaSeGPUFallbackAPI:
    """Get or create ChiaSeGPU API instance."""
    global _chiasegpu_api_instance
    if _chiasegpu_api_instance is None:
        _chiasegpu_api_instance = ChiaSeGPUFallbackAPI()
        logger.info("✅ ChiaSeGPU Fallback API initialized")
    return _chiasegpu_api_instance
