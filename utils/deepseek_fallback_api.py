"""
DeepSeek API Fallback Module
Handles communication with DeepSeek API (Primary Fallback)
"""

import logging
import os
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_deepseek_fallback_api():
    """Factory function to get DeepSeek API instance."""
    return DeepseekFallbackAPI()


class DeepseekFallbackAPI:
    """Handles DeepSeek API calls for chatbot fallback (Primary priority)."""

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
        major_list: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """Build chat messages for the DeepSeek API."""
        conversation_history = self._format_conversation_history(history)

        if context == "chatbot":
            system_prompt = """Bạn là chatbot tư vấn ngành học cho sinh viên Việt Nam.
Nhiệm vụ của bạn là trả lời dựa trên ngữ cảnh hội thoại gần nhất và câu hỏi hiện tại của người dùng.

Quy tắc:
- Trả lời bằng tiếng Việt, tự nhiên, thân thiện.
- Ưu tiên 2-4 câu ngắn gọn hoặc 1 đoạn ngắn.
- Không dùng tiêu đề, không đánh số mục, không liệt kê theo dàn ý trừ khi người dùng yêu cầu rõ ràng.
- Nếu người dùng đang hỏi tiếp một ý trước đó, hãy dùng ngữ cảnh hội thoại để hiểu đối tượng/ngành đang được nhắc tới.
- Nếu thiếu ngữ cảnh quan trọng, hỏi lại đúng 1 câu ngắn để làm rõ.
- Không nhắc rằng bạn đang làm theo prompt hay quy tắc nội bộ."""
        else:
            system_prompt = "Bạn là một trợ lý AI hữu ích. Trả lời bằng tiếng Việt."

        context_hints = []
        if active_major:
            context_hints.append(f"Ngành đang được nhắc tới: {active_major}")
        if active_topic:
            context_hints.append(f"Chủ đề hiện tại: {active_topic}")

        hint_block = "\n".join(context_hints).strip()

        if conversation_history:
            user_content = f"Ngữ cảnh hội thoại gần nhất:\n{conversation_history}\n\n"
            if hint_block:
                user_content += f"{hint_block}\n\n"
            user_content += f"Câu hỏi hiện tại:\n{user_text}"
        elif hint_block:
            user_content = f"{hint_block}\n\nCâu hỏi hiện tại:\n{user_text}"
        else:
            user_content = user_text

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def __init__(self, env_prefix: str = "DEEPSEEK"):
        """Initialize DeepSeek API client."""
        self.env_prefix = str(env_prefix or "DEEPSEEK").strip().upper()
        self.api_key = os.getenv(f"{self.env_prefix}_API_KEY", "")
        self.base_url = os.getenv(f"{self.env_prefix}_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv(f"{self.env_prefix}_MODEL", "deepseek-chat")
        
        if not self.api_key:
            logger.warning("⚠️ %s_API_KEY not found in environment variables", self.env_prefix)
        
        # Initialize OpenAI client (DeepSeek uses OpenAI-compatible API)
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info("✓ %s API client initialized (PRIMARY PRIORITY)", self.env_prefix)
        except Exception as e:
            logger.error("✗ Failed to initialize %s client: %s", self.env_prefix, e)
            self.client = None

    def analyze_free_text(
        self,
        user_text: str,
        context: str = "chatbot",
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
        major_list: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send user text to DeepSeek API and get response.
        
        Args:
            user_text: The user's input text
            context: Context for the API (e.g., "chatbot")
            history: Chat history for context
            active_major: Currently active major (if any)
            active_topic: Currently active topic (if any)
            major_list: List of available majors for constraint
            
        Returns:
            Dict with success status and response text
        """
        if not self.client:
            return {
                "success": False,
                "response": "",
                "error": "DeepSeek client not initialized"
            }
        
        if not user_text or not user_text.strip():
            return {
                "success": False,
                "response": "",
                "error": "Empty user text"
            }
        
        try:
            messages = self._build_prompt(
                user_text,
                context=context,
                history=history,
                active_major=active_major,
                active_topic=active_topic,
                major_list=major_list,
            )

            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5 if context == "chatbot" else 0.2,
                max_tokens=500,
                top_p=0.9
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            
            logger.info(f"✓ DeepSeek API response generated (length: {len(response_text)})")
            
            return {
                "success": True,
                "response": response_text,
                "model": self.model,
                "source": f"{self.env_prefix.lower()}_fallback",
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
        
        except Exception as e:
            logger.error(f"✗ DeepSeek API error: {e}", exc_info=True)
            return {
                "success": False,
                "response": "",
                "error": str(e)
            }

    def test_connection(self) -> bool:
        """Test if DeepSeek API connection is working."""
        try:
            response = self.analyze_free_text("Hello!", context="test")
            is_working = response.get("success", False)
            
            if is_working:
                logger.info("✓ DeepSeek API connection test: SUCCESS")
            else:
                logger.warning(f"✗ DeepSeek API connection test: FAILED - {response.get('error', 'Unknown error')}")
            
            return is_working
        except Exception as e:
            logger.error(f"✗ DeepSeek API connection test error: {e}")
            return False
