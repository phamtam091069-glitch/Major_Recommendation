"""
Chatbot module for major recommendation system.
Uses model-based TF-IDF matching and fallback to external API if needed.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sklearn.metrics.pairwise import cosine_similarity

from .claude_fallback_api import get_claude_fallback_api
from .constants import BASE_DIR, MAJOR_DISPLAY, SUGGESTION_VI

MAJOR_EXTRA_ALIAS_MAP = {
    "Cong nghe thong tin": ["cntt", "it", "information technology"],
}

MARINE_ALIAS_MAP = {
    "Dieu khien va quan ly tau bien": [
        "điều khiển và quản lý tàu biển",
        "quản lý tàu biển",
        "điều khiển tàu biển",
        "lái tàu",
        "Lái tàu",
        "hàng hải",
        "ngành hàng hải",
        "tàu biển",
        "tàu thủy",
        "ship control",
        "ship control and management",
        "ship management",
        "ship navigation",
        "marine navigation",
        "maritime",
        "maritime studies",
        "maritime management",
        "nautical",
        "nautical science",
        "quản lý hàng hải",
        "sĩ quan hàng hải",
        "sĩ quan boong",
        "deck officer",
        "ship officer",
        "seafaring",
        "vessel navigation",
        "ship handling",
        "vessel handling",
        "vận tải biển",
        "quản lý vận hành tàu biển",
    ],
    "Khai thac may tau thuy va quan ly ky thuat": [
        "khai thác máy tàu thủy và quản lý kỹ thuật",
        "khai thac may tau thuy va quan ly ky thuat",
        "khai thác máy tàu thủy",
        "quản lý kỹ thuật tàu thủy",
        "máy tàu thủy",
        "máy tàu",
        "ngành máy tàu thủy",
        "ngành khai thác máy tàu thủy",
        "ngành quản lý kỹ thuật tàu thủy",
        "thuyền máy",
        "sĩ quan máy tàu",
        "máy trưởng",
        "engine room",
        "marine engineering",
        "marine machinery",
        "marine technical management",
        "marine technical operations",
        "ship engineering",
        "ship machinery",
        "ship engine room",
        "ship engine management",
        "ship maintenance",
        "ship repair",
        "engine officer",
        "engineering officer",
        "marine officer engine",
        "vessel engineering",
        "vessel machinery",
        "marine propulsion",
        "marine power system",
        "hàng hải kỹ thuật",
        "cơ điện tàu thủy",
        "kỹ thuật tàu thủy",
        "kỹ thuật máy tàu",
        "quản lý máy tàu",
        "bảo trì máy tàu thủy",
        "sửa chữa máy tàu thủy",
    ],
}
from .openai_fallback_api import get_openai_fallback_api
from .predictor import Predictor

logger = logging.getLogger(__name__)


class MajorChatbot:
    """Chatbot that answers questions about majors."""

    def __init__(self, predictor: Predictor):
        self.predictor = predictor
        self.tfidf = predictor.tfidf
        self.major_vectors = predictor.major_vectors
        self.major_names = predictor.major_names
        self.major_lookup = predictor.major_lookup
        self.CONFIDENCE_THRESHOLD = 0.5
        self.salary_benchmarks = self._load_salary_benchmarks()

        self.greeting_responses = {
            "xin chào": "Xin chào! 👋 Mình là chatbot tư vấn ngành học. Bạn muốn biết gì về các ngành học?",
            "hi": "Xin chào! 👋 Mình sẵn sàng giúp bạn tìm ngành học phù hợp. Hỏi gì đi nào!",
            "hello": "Xin chào! 👋 Bạn muốn tìm hiểu thêm về ngành nào?",
            "helo": "Xin chào! 👋 Hãy hỏi mình về các ngành học!",
        }

        self.qa_patterns = {
            "công nghệ": "💻 3 ngành nổi bật:\n1️⃣ Công nghệ thông tin\n2️⃣ Khoa học dữ liệu\n3️⃣ An ninh mạng\n\nHợp nếu bạn thích lập trình và logic.",
            "máy tính": "💻 3 ngành máy tính:\n1️⃣ Công nghệ thông tin\n2️⃣ Khoa học dữ liệu\n3️⃣ Kỹ thuật máy tính\n\nNhu cầu cao, cơ hội tốt.",
            "kỹ thuật": "⚙️ 3 ngành kỹ thuật:\n1️⃣ Cơ khí\n2️⃣ Điện - điện tử\n3️⃣ Xây dựng\n\nHợp nếu bạn thích thực hành và tư duy logic.",
            "kinh doanh": "💼 3 ngành kinh doanh:\n1️⃣ Quản trị kinh doanh\n2️⃣ Marketing\n3️⃣ Tài chính - ngân hàng\n\nPhù hợp nếu bạn mạnh giao tiếp và quản lý.",
            "ngôn ngữ": "🌍 3 ngành ngôn ngữ:\n1️⃣ Tiếng Anh\n2️⃣ Tiếng Trung\n3️⃣ Tiếng Nhật\n\nTốt cho giao tiếp và môi trường quốc tế.",
            "sức khỏe": "🏥 3 ngành sức khỏe:\n1️⃣ Y dược\n2️⃣ Điều dưỡng\n3️⃣ Dinh dưỡng\n\nHợp nếu bạn thích chăm sóc con người.",
            "du lịch": "✈️ 3 ngành du lịch:\n1️⃣ Quản lý du lịch\n2️⃣ Hướng dẫn du lịch\n3️⃣ Thiết kế tour\n\nHợp nếu bạn thích giao tiếp và khám phá.",
            "giáo dục": "📚 3 ngành giáo dục:\n1️⃣ Sư phạm Toán\n2️⃣ Sư phạm Anh\n3️⃣ Sư phạm Khoa học\n\nPhù hợp nếu bạn thích dạy học.",
            "thiết kế": "🎨 3 ngành thiết kế:\n1️⃣ Thiết kế đồ họa\n2️⃣ Thiết kế thời trang\n3️⃣ Thiết kế nội thất\n\nHợp nếu bạn có óc sáng tạo và thẩm mỹ.",
        }

    def _normalize_input(self, text: str) -> str:
        return str(text or "").strip().lower()

    def _normalize_for_lookup(self, text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "").strip().lower())

    def _limit_to_top3_majors(self, text: str) -> str:
        lines = str(text or "").split("\n")
        result_lines = []
        for line in lines:
            if re.search(r"^#+\s*[4-9][\.\s]", line.strip()):
                break
            result_lines.append(line)
        return "\n".join(result_lines).strip()

    def _make_response_concise(self, text: str) -> str:
        if not text:
            return text

        text = re.sub(r"\n{3,}", "\n\n", str(text)).strip()
        text = re.sub(r"[ \t]+", " ", text)

        max_chars = 1200
        if len(text) <= max_chars:
            return text

        cut_at = max(
            text.rfind(". ", 0, max_chars),
            text.rfind("! ", 0, max_chars),
            text.rfind("? ", 0, max_chars),
            text.rfind("\n", 0, max_chars),
        )
        if cut_at < 300:
            cut_at = max_chars

        result = text[:cut_at].rstrip()
        if result and result[-1] not in ".!?":
            result += "..."
        return result

    def _format_major_description(self, text: str) -> str:
        """Chuẩn hóa mô tả ngành thành các gạch đầu dòng ngắn, dễ đọc."""
        cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
        if not cleaned:
            return ""

        # Tách câu trước, rồi tách thêm theo dấu phẩy/chấm phẩy để tạo bullet ngắn.
        sentence_chunks = re.split(r"(?<=[.!?])\s+", cleaned)
        items: List[str] = []
        for sentence in sentence_chunks:
            sentence = sentence.strip().strip("•-")
            if not sentence:
                continue
            sub_parts = [p.strip() for p in re.split(r"\s*[,;:]\s*", sentence) if p.strip()]
            for part in sub_parts:
                part = part.strip()
                if not part:
                    continue
                if len(part.split()) > 18:
                    tokens = part.split()
                    midpoint = len(tokens) // 2
                    part = f"{' '.join(tokens[:midpoint])}. {' '.join(tokens[midpoint:])}"
                if part[-1] not in '.!?':
                    part += '.'
                items.append(part)

        if not items:
            return cleaned if cleaned.endswith(('.', '!', '?')) else cleaned + '.'

        return "\n".join(f"• {item}" for item in items)

    def _build_major_bullet_reply(self, major_key: str, source_text: str = "") -> str:
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        cleaned_desc = re.sub(r"\s+", " ", str(source_text or "")).strip()
        if cleaned_desc:
            return (
                f"Ngành {major_display} tập trung vào {cleaned_desc}. "
                f"Nếu bạn muốn, mình có thể nói kỹ hơn theo từng phần như học gì, chi phí, mức độ khó và cơ hội việc làm."
            )
        return (
            f"Mình có thể chia sẻ về ngành {major_display} theo hướng dễ hiểu hơn, "
            f"ví dụ học gì, có khó không, chi phí và cơ hội việc làm."
        )

    def _sanitize_fallback_response(self, text: str) -> str:
        """Làm phẳng các câu trả lời có cấu trúc để tránh dàn ý quá cứng."""
        if not text:
            return text

        lines = []
        for raw_line in str(text).splitlines():
            line = raw_line.strip()
            if not line:
                continue

            line = re.sub(r"^\s*(?:[-*•]|#+|\d+[).\]]?)\s*", "", line)
            line = re.sub(
                r"^(Mô tả ngành|Kỹ năng cần thiết|Cơ hội việc làm|Lương(?: và phúc lợi)?|Những gợi ý liên quan|Gợi ý liên quan)\s*[:\-]?\s*",
                "",
                line,
                flags=re.IGNORECASE,
            )
            if line:
                lines.append(line)

        text = " ".join(lines)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return self._make_response_concise(text)

    def _is_greeting(self, text: str) -> Optional[str]:
        norm_text = self._normalize_input(text)
        for greeting_key, response in self.greeting_responses.items():
            if re.search(r"\b" + re.escape(greeting_key) + r"\b", norm_text):
                return response
        return None

    def _check_pattern_match(self, text: str) -> Optional[str]:
        norm_text = self._normalize_input(text)
        for pattern_key, response in self.qa_patterns.items():
            if pattern_key in norm_text:
                return response
        return None

    def _is_off_topic_personal(self, text: str) -> bool:
        """Nhận diện câu hỏi ngoài phạm vi tư vấn ngành (chuyện tình cảm cá nhân)."""
        norm_text = self._normalize_input(text)
        if not norm_text:
            return False

        romance_patterns = [
            r"\bngười yêu\b",
            r"\btỏ tình\b",
            r"\bcrush\b",
            r"\bhẹn hò\b",
            r"\byêu\b",
            r"\bny\b",
            r"\bbạn gái\b",
            r"\bbạn trai\b",
            r"\bcưa\b",
            r"\bthả thính\b",
            r"\bthích\s+\w+\b",
        ]
        return any(re.search(pattern, norm_text) for pattern in romance_patterns)

    def _build_scope_guard_reply(self) -> str:
        return (
            "Mình chuyên tư vấn ngành học và định hướng nghề nghiệp nên không phù hợp để tư vấn chuyện tình cảm cá nhân. "
            "Bạn có thể hỏi mình về ngành phù hợp với sở thích/năng lực, học gì, học phí, cơ hội việc làm hoặc mức lương nhé."
        )

    def _is_followup_question(self, text: str) -> bool:
        norm_text = self._normalize_input(text)
        followup_patterns = [
            r"\bngành này\b",
            r"\bngành đó\b",
            r"\bngành ấy\b",
            r"\bngành kia\b",
            r"\bngành trên\b",
            r"\bnày\b",
            r"\bđó\b",
            r"\bnó\b",
            r"\blương\b",
            r"\bhọc phí\b",
            r"\bchi phí\b",
            r"\bcần tiền\b",
            r"\btốn tiền\b",
            r"\bđắt\b",
            r"\bđắt không\b",
            r"\bđiểm chuẩn\b",
            r"\bcơ hội việc làm\b",
            r"\bđầu ra\b",
            r"\bkhó không\b",
            r"\bcó khó không\b",
            r"\bphù hợp không\b",
            r"\bthời gian học\b",
            r"\bở đâu\b",
            r"\bnên học\b",
            r"\bcó nên\b",
            r"\bhọc gì\b",
            r"\bhọc những gì\b",
            r"\bmôn gì\b",
            r"\byếu tố nào\b",
            r"\btố chất\b",
            r"\bcần gì\b",
            r"\bphù hợp với ai\b",
        ]
        return any(re.search(pattern, norm_text) for pattern in followup_patterns)

    def _find_major_in_text(self, text: str) -> str:
        norm_text = self._normalize_for_lookup(text)
        if not norm_text:
            return ""

        candidates: List[Tuple[str, str]] = []
        for major_key in self.major_names:
            candidates.append((major_key, self._normalize_for_lookup(major_key)))
            candidates.append((major_key, self._normalize_for_lookup(MAJOR_DISPLAY.get(major_key, major_key))))
            for alias in MAJOR_EXTRA_ALIAS_MAP.get(major_key, []):
                candidates.append((major_key, self._normalize_for_lookup(alias)))
            for alias in MARINE_ALIAS_MAP.get(major_key, []):
                candidates.append((major_key, self._normalize_for_lookup(alias)))

        for major_key, major_name in sorted(candidates, key=lambda x: len(x[1]), reverse=True):
            if major_name and major_name in norm_text:
                return major_key
        return ""

    def _find_major_candidates_in_text(self, text: str) -> List[str]:
        """Tìm tất cả major xuất hiện trong text theo thứ tự xuất hiện trong câu người dùng."""
        norm_text = self._normalize_for_lookup(text)
        if not norm_text:
            return []

        major_first_pos: Dict[str, int] = {}
        for major_key in self.major_names:
            aliases = [
                self._normalize_for_lookup(major_key),
                self._normalize_for_lookup(MAJOR_DISPLAY.get(major_key, major_key)),
            ]
            aliases.extend(self._normalize_for_lookup(alias) for alias in MAJOR_EXTRA_ALIAS_MAP.get(major_key, []))
            aliases.extend(self._normalize_for_lookup(alias) for alias in MARINE_ALIAS_MAP.get(major_key, []))

            best_pos: Optional[int] = None
            for alias in aliases:
                if not alias:
                    continue
                pos = norm_text.find(alias)
                if pos == -1:
                    continue
                if best_pos is None or pos < best_pos:
                    best_pos = pos

            if best_pos is not None:
                major_first_pos[major_key] = best_pos

        return [major for major, _pos in sorted(major_first_pos.items(), key=lambda item: item[1])]

    def _get_major_aliases(self, major_key: str) -> List[str]:
        aliases = {
            self._normalize_for_lookup(major_key),
            self._normalize_for_lookup(MAJOR_DISPLAY.get(major_key, major_key)),
        }
        aliases.update(self._normalize_for_lookup(alias) for alias in MAJOR_EXTRA_ALIAS_MAP.get(major_key, []))
        aliases.update(self._normalize_for_lookup(alias) for alias in MARINE_ALIAS_MAP.get(major_key, []))
        return sorted([alias for alias in aliases if alias], key=len, reverse=True)

    def _is_major_selection_reply(self, text: str, major_key: str) -> bool:
        """Phát hiện câu trả lời ngắn kiểu chọn 1 ngành (vd: 'Công nghệ thông tin')."""
        if not text or not major_key:
            return False

        norm_text = self._normalize_for_lookup(text)
        cleaned_text = self._normalize_for_lookup(re.sub(r"[^\w\s]", " ", norm_text, flags=re.UNICODE))
        if not cleaned_text:
            return False

        filler_tokens = {
            "em", "anh", "chi", "chị", "toi", "tôi", "minh", "mình", "chon", "chọn",
            "nganh", "ngành", "la", "là", "thi", "thì", "ve", "về", "nhe", "nhé", "nha", "ạ", "a",
            "ha", "vay", "vậy", "xin", "cho", "di", "đi", "duoc", "được", "nhe", "nhé",
        }

        for alias in self._get_major_aliases(major_key):
            if alias and alias in cleaned_text:
                remaining = self._normalize_for_lookup(cleaned_text.replace(alias, " "))
                if not remaining:
                    return True
                tokens = remaining.split()
                if len(tokens) <= 6 and all(token in filler_tokens for token in tokens):
                    return True

        return False

    def _build_ambiguity_clarification(self, major_a: str, major_b: str) -> str:
        display_a = MAJOR_DISPLAY.get(major_a, major_a)
        display_b = MAJOR_DISPLAY.get(major_b, major_b)
        return f"Bạn đang hỏi về {display_a} hay {display_b}?"

    def _extract_recent_context(
        self,
        history: Optional[List[Dict[str, Any]]],
        current_message: str = "",
    ) -> str:
        if not history:
            return ""

        current_norm = self._normalize_for_lookup(current_message)
        for item in reversed(history):
            if not isinstance(item, dict):
                continue
            if item.get("role") != "user":
                continue

            content = str(item.get("content", "")).strip()
            if not content:
                continue
            if current_norm and self._normalize_for_lookup(content) == current_norm:
                continue
            return content

        return ""

    def _extract_context_major(
        self,
        history: Optional[List[Dict[str, Any]]],
        current_message: str = "",
    ) -> str:
        """Lấy ngành đang được nói tới gần nhất theo thứ tự tin nhắn gần nhất → cũ hơn."""
        current_major = self._find_major_in_text(current_message)
        if current_major:
            return current_major
        if not history:
            return ""

        current_norm = self._normalize_for_lookup(current_message)
        recent_history = list(history)[-20:]

        # Ưu tiên tin nhắn gần nhất trước, rồi lùi dần tới tin nhắn cũ hơn.
        for item in reversed(recent_history):
            if not isinstance(item, dict):
                continue

            content = str(item.get("content", "")).strip()
            if not content:
                continue
            if current_norm and self._normalize_for_lookup(content) == current_norm:
                continue

            major_key = self._find_major_in_text(content)
            if major_key:
                return major_key

        return ""

    def _build_history_summary(self, history: Optional[List[Dict[str, Any]]], max_items: int = 4) -> str:
        """Tóm tắt ngắn các lượt hội thoại gần nhất để làm rõ ngữ cảnh."""
        if not history:
            return ""

        summary_lines: List[str] = []
        for item in history[-max_items:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "")).strip()
            content = str(item.get("content", "")).strip()
            if role not in {"user", "assistant"} or not content:
                continue
            label = "Người dùng" if role == "user" else "Trợ lý"
            summary_lines.append(f"{label}: {content}")

        return "\n".join(summary_lines)

    def _build_context_packet(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> str:
        """Đóng gói ngữ cảnh ngắn gọn cho fallback model."""
        history_summary = self._build_history_summary(history)
        major_display = MAJOR_DISPLAY.get(active_major, active_major) if active_major else ""
        topic_display = active_topic or ""

        context_parts = []
        if major_display:
            context_parts.append(f"Ngành đang được nhắc tới: {major_display}")
        if topic_display:
            context_parts.append(f"Chủ đề đang hỏi: {topic_display}")
        if history_summary:
            context_parts.append(f"Tóm tắt hội thoại gần nhất:\n{history_summary}")
        context_parts.append(f"Câu hỏi hiện tại: {user_message}")

        return "\n\n".join(context_parts).strip()

    def _detect_numeric_question(self, user_message: str) -> bool:
        norm_text = self._normalize_input(user_message)
        numeric_patterns = [
            r"\bsố liệu\b",
            r"\bbao nhiêu\b",
            r"\bmức lương\b",
            r"\blương\b",
            r"\bhọc phí\b",
            r"\bthu nhập\b",
            r"\btỷ lệ\b",
            r"\bphần trăm\b",
            r"\bthống kê\b",
            r"\bsố lượng\b",
            r"\bđiểm chuẩn\b",
            r"\bcó số liệu\b",
        ]
        return any(re.search(pattern, norm_text) for pattern in numeric_patterns)

    def _extract_source_numeric_fact(self, major_key: str, feedback_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Lấy dữ liệu số liệu thật nếu có từ nguồn nội bộ."""
        if not major_key or not isinstance(feedback_data, dict):
            return None

        majors = feedback_data.get("majors", {}) or {}
        major_entry = majors.get(major_key, {}) if isinstance(majors, dict) else {}
        if not isinstance(major_entry, dict):
            return None

        numeric_fields = ["salary", "tuition", "salary_range", "average_salary", "median_salary", "scholarship", "employment_rate", "acceptance_rate"]
        for field in numeric_fields:
            value = major_entry.get(field)
            if value not in (None, "", []):
                return f"Dữ liệu nội bộ cho {MAJOR_DISPLAY.get(major_key, major_key)}: {field} = {value}."

        stats = feedback_data.get("major_stats", {})
        if isinstance(stats, dict):
            major_stats = stats.get(major_key, {})
            if isinstance(major_stats, dict):
                for field in numeric_fields:
                    value = major_stats.get(field)
                    if value not in (None, "", []):
                        return f"Dữ liệu nội bộ cho {MAJOR_DISPLAY.get(major_key, major_key)}: {field} = {value}."

        return None

    def _load_salary_benchmarks(self) -> Dict[str, Any]:
        """Nạp dữ liệu benchmark lương theo ngành từ file JSON."""
        default_payload: Dict[str, Any] = {"metadata": {}, "majors": {}}
        file_path = Path(BASE_DIR) / "data" / "salary_benchmarks.json"
        try:
            if not file_path.exists():
                return default_payload
            with file_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                return default_payload
            metadata = payload.get("metadata", {})
            majors = payload.get("majors", {})
            if not isinstance(metadata, dict):
                metadata = {}
            if not isinstance(majors, dict):
                majors = {}
            return {
                "metadata": metadata,
                "majors": majors,
            }
        except Exception as exc:
            logger.warning("Failed to load salary benchmarks: %s", exc)
            return default_payload

    def _get_salary_disclaimer(self) -> str:
        metadata = self.salary_benchmarks.get("metadata", {}) if isinstance(self.salary_benchmarks, dict) else {}
        disclaimer = metadata.get("disclaimer") if isinstance(metadata, dict) else None
        return str(disclaimer).strip() if disclaimer else "Số liệu trên chỉ mang tính chất tham khảo tùy thuộc vào thị trường việc làm."

    def _get_general_salary_sources(self) -> List[str]:
        metadata = self.salary_benchmarks.get("metadata", {}) if isinstance(self.salary_benchmarks, dict) else {}
        general_sources = metadata.get("general_sources", []) if isinstance(metadata, dict) else []
        if not isinstance(general_sources, list):
            return []
        return [str(src).strip() for src in general_sources if str(src).strip()]

    def _build_salary_benchmark_reply(self, major_key: str) -> Optional[str]:
        if not major_key:
            return None

        benchmarks = self.salary_benchmarks.get("majors", {}) if isinstance(self.salary_benchmarks, dict) else {}
        major_payload = benchmarks.get(major_key, {}) if isinstance(benchmarks, dict) else {}
        if not isinstance(major_payload, dict) or not major_payload:
            return None

        salary_by_level = major_payload.get("salary_by_level", {})
        if not isinstance(salary_by_level, dict):
            return None

        junior = str(salary_by_level.get("junior", "")).strip()
        middle = str(salary_by_level.get("middle", "")).strip()
        senior = str(salary_by_level.get("senior", "")).strip()
        if not any([junior, middle, senior]):
            return None

        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        updated_at = str(major_payload.get("updated_at", "")).strip()
        sources = major_payload.get("sources", [])
        notes = major_payload.get("notes", [])

        lines = [f"Mức lương tham khảo của ngành {major_display} theo cấp độ:"]
        if junior:
            lines.append(f"• Junior (0-2 năm): khoảng {junior}/tháng.")
        if middle:
            lines.append(f"• Middle (2-5 năm): khoảng {middle}/tháng.")
        if senior:
            lines.append(f"• Senior (5+ năm): khoảng {senior}/tháng.")

        if updated_at:
            lines.append(f"Kỳ cập nhật dữ liệu: {updated_at}.")

        if isinstance(sources, list) and sources:
            clean_sources = [str(src).strip() for src in sources if str(src).strip()]
            if clean_sources:
                lines.append("Nguồn tham khảo (benchmark ngành): " + "; ".join(clean_sources) + ".")

        if isinstance(notes, list) and notes:
            clean_notes = [str(note).strip() for note in notes if str(note).strip()]
            for note in clean_notes[:2]:
                lines.append(f"• Lưu ý: {note}")

        lines.append(self._get_salary_disclaimer())
        return "\n".join(lines)

    def _build_salary_estimate_reply(self, major_key: str) -> str:
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        major_norm = self._normalize_for_lookup(major_display)

        if any(token in major_norm for token in ["công nghệ thông tin", "du lieu", "ai", "an ninh mang", "ky thuat phan mem"]):
            entry_range = "10-18 triệu/tháng"
            mid_range = "18-35 triệu/tháng"
            senior_range = "35-60+ triệu/tháng"
        elif any(token in major_norm for token in ["tàu", "hàng hải", "tau thuy", "marine", "maritime"]):
            entry_range = "12-22 triệu/tháng"
            mid_range = "22-45 triệu/tháng"
            senior_range = "45-80+ triệu/tháng"
        else:
            entry_range = "8-15 triệu/tháng"
            mid_range = "15-28 triệu/tháng"
            senior_range = "28-50+ triệu/tháng"

        lines = [
            f"Ước lượng mức lương của ngành {major_display} theo kinh nghiệm/vị trí:",
            f"• Mới ra trường / Junior: khoảng {entry_range}.",
            f"• 2-5 năm kinh nghiệm / Middle: khoảng {mid_range}.",
            f"• Senior / Lead / Chuyên gia: khoảng {senior_range}.",
        ]

        general_sources = self._get_general_salary_sources()
        if general_sources:
            lines.append("Nguồn tham khảo chung: " + "; ".join(general_sources) + ".")
        lines.append("Chưa có benchmark riêng cho ngành này, mức trên là ước lượng theo nhóm ngành liên quan.")
        lines.append(self._get_salary_disclaimer())
        return "\n".join(lines)

    def _detect_followup_topic(self, user_message: str) -> str:
        norm_text = self._normalize_input(user_message)
        if any(key in norm_text for key in ["lương", "thu nhập", "tiền lương"]):
            return "salary"
        if any(key in norm_text for key in ["khó", "có khó không", "độ khó"]):
            return "difficulty"
        if any(key in norm_text for key in ["học phí", "chi phí", "cần tiền", "tốn tiền", "đắt", "đắt không"]):
            return "tuition"
        if any(key in norm_text for key in ["việc làm", "đầu ra", "cơ hội việc làm"]):
            return "career"
        if any(key in norm_text for key in ["thời gian học", "mấy năm", "bao lâu"]):
            return "duration"
        if any(key in norm_text for key in ["học gì", "học những gì", "môn gì", "học môn gì"]):
            return "study_content"
        if any(key in norm_text for key in ["yếu tố nào", "tố chất", "cần gì", "phù hợp với ai", "năng lực nào"]):
            return "fit_factors"
        if any(key in norm_text for key in ["ngành đó", "ngành này", "ngành ấy", "ngành kia", "biết thêm", "thêm gì"]):
            return "overview"
        return ""

    def _build_contextual_followup_reply(self, topic: str, major_key: str, feedback_data: Optional[Dict[str, Any]] = None) -> str:
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        major_info = self.major_lookup.get(major_key, {})
        major_desc = str(major_info.get("mo_ta", "")).strip()
        source_numeric_fact = self._extract_source_numeric_fact(major_key, feedback_data=feedback_data)

        if topic == "salary":
            benchmark_reply = self._build_salary_benchmark_reply(major_key)
            if benchmark_reply:
                return benchmark_reply
            if source_numeric_fact:
                return f"{source_numeric_fact}\n{self._get_salary_disclaimer()}"
            return self._build_salary_estimate_reply(major_key)
        if topic == "difficulty":
            return (
                f"Độ khó của ngành {major_display} phụ thuộc khá nhiều vào nền tảng học tập và mức độ phù hợp của bạn với ngành.\n"
                f"• Nếu cần, mình có thể mô tả theo học phần, kỹ năng và môi trường đào tạo thay vì đưa số liệu ước đoán."
            )
        if topic == "tuition":
            if source_numeric_fact:
                return (
                    f"Về chi phí học ngành {major_display}, hiện mình có dữ liệu nội bộ như sau: {source_numeric_fact} "
                    f"Nếu bạn muốn, mình có thể giúp bạn ước lượng thêm tổng chi phí theo từng năm học."
                )
            return (
                f"Có nhé, học ngành {major_display} chắc chắn sẽ cần chi phí. "
                f"Mức cụ thể phụ thuộc vào trường, chương trình (chuẩn/chất lượng cao), và các khoản thực hành. "
                f"Nếu bạn gửi tên trường bạn quan tâm, mình sẽ giúp bạn bóc tách học phí và khoản phát sinh theo hướng dễ hình dung hơn."
            )
        if topic == "career":
            return (
                f"Với ngành {major_display}, cơ hội việc làm phụ thuộc nhiều vào kỹ năng thực hành, thực tập và ngoại ngữ.\n"
                f"• Có thể làm trong doanh nghiệp.\n"
                f"• Có thể làm ở cơ quan/chuyên môn kỹ thuật.\n"
                f"• Có thể đi theo hướng dự án hoặc môi trường quốc tế."
            )
        if topic == "duration":
            return (
                f"Thông thường ngành {major_display} học khoảng 4 năm ở bậc đại học, nhưng còn tùy chương trình.\n"
                f"• Có thể có thực tập hoặc học phần chuyên sâu.\n"
                f"• Một số trường có lộ trình khác nhau theo hệ đào tạo.\n"
                f"Nếu bạn muốn, mình có thể nói rõ theo từng trường cụ thể."
            )
        if topic == "study_content":
            suggestion = str(SUGGESTION_VI.get(major_key, "")).strip()
            parts = [f"Với ngành {major_display}, bạn sẽ học các khối kiến thức cốt lõi sau:"]
            if major_desc:
                parts.append(self._format_major_description(major_desc))
            else:
                parts.append("• Kiến thức nền tảng và học phần chuyên ngành theo định hướng đào tạo của trường.")
            if suggestion:
                parts.append(f"Gợi ý chuẩn bị: {suggestion}")
            return "\n".join(parts)
        if topic == "fit_factors":
            major_norm = self._normalize_for_lookup(major_display)
            if any(token in major_norm for token in ["tàu", "hàng hải", "tau thuy", "marine", "maritime"]):
                return (
                    f"Nếu muốn theo ngành {major_display}, bạn nên có các yếu tố sau:\n"
                    f"• Sức khỏe tốt và khả năng thích nghi môi trường làm việc trên biển.\n"
                    f"• Tính kỷ luật, tuân thủ quy trình an toàn hàng hải.\n"
                    f"• Bình tĩnh xử lý tình huống và ra quyết định nhanh khi có sự cố.\n"
                    f"• Nền tảng tiếng Anh chuyên ngành để học tài liệu và làm việc quốc tế.\n"
                    f"• Tinh thần chịu áp lực, có trách nhiệm và sẵn sàng làm việc xa nhà theo hải trình."
                )
            return (
                f"Để học tốt ngành {major_display}, bạn nên có:\n"
                f"• Sự quan tâm thật sự với lĩnh vực ngành học.\n"
                f"• Tư duy logic/giải quyết vấn đề và tinh thần tự học.\n"
                f"• Kỹ năng giao tiếp, làm việc nhóm và quản lý thời gian.\n"
                f"• Kỷ luật học tập và khả năng chịu áp lực trong giai đoạn thực tập/làm dự án."
            )

        if major_desc:
            return self._build_major_bullet_reply(major_key, major_desc)
        return f"Mình có thể nói thêm về ngành {major_display} nếu bạn muốn hỏi sâu hơn về học gì, làm gì hoặc cơ hội việc làm."

    def _get_tfidf_response(self, text: str) -> Tuple[Optional[str], float]:
        try:
            user_vector = self.tfidf.transform([text])
            similarities = cosine_similarity(user_vector, self.major_vectors)[0]
            best_idx = similarities.argmax()
            best_score = float(similarities[best_idx])
            best_major = self.major_names[best_idx]

            if best_score < self.CONFIDENCE_THRESHOLD:
                return None, best_score

            major_info = self.major_lookup.get(best_major, {})
            major_display = MAJOR_DISPLAY.get(best_major, major_info.get("major_display", best_major))
            major_desc = major_info.get("mo_ta", "")

            if major_desc:
                response = (
                    f"🎯 **{major_display}**\n\n"
                    f"{major_desc}\n\n"
                    f"💡 Phù hợp nếu bạn thích ngành này."
                )
            else:
                response = f"🎯 **{major_display}**\n\n💡 Phù hợp nếu bạn thích ngành này."
            return self._make_response_concise(response), best_score
        except Exception as exc:
            logger.exception("Error in TF-IDF response: %s", exc)
            return None, 0.0

    def _get_fallback_response(
        self,
        text: str,
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
        active_topic: str = "",
    ) -> str:
        fallback_input = self._build_context_packet(
            user_message=text,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
        )
        try:
            openai_api = get_openai_fallback_api()
            result = openai_api.analyze_free_text(
                fallback_input,
                context="chatbot",
                history=history,
                active_major=active_major,
                active_topic=active_topic,
            )
            if isinstance(result, dict) and result.get("success"):
                response_text = str(result.get("response", "")).strip()
                if response_text:
                    response_text = self._limit_to_top3_majors(response_text)
                    return self._sanitize_fallback_response(response_text)
        except Exception as exc:
            logger.warning(f"OpenAI API failed, trying Claude: {exc}")

        try:
            claude_api = get_claude_fallback_api()
            result = claude_api.analyze_free_text(
                fallback_input,
                context="chatbot",
                history=history,
                active_major=active_major,
                active_topic=active_topic,
            )
            if isinstance(result, dict) and result.get("success"):
                response_text = str(result.get("response", "")).strip()
                if response_text:
                    response_text = self._limit_to_top3_majors(response_text)
                    return self._sanitize_fallback_response(response_text)
        except Exception as exc:
            logger.warning(f"Claude API also failed: {exc}")

        response = f"""
Mình chưa chắc về câu hỏi của bạn ({text}).

Bạn có thể:
1. Điền form để nhận gợi ý chính xác hơn
2. Hỏi rõ về ngành cụ thể
3. Tiếp tục chat để mình hỗ trợ thêm
        """.strip()
        return self._make_response_concise(response)

    def _build_contextual_message(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        if not self._is_followup_question(user_message):
            return user_message

        recent_context = self._extract_recent_context(history, current_message=user_message)
        if not recent_context:
            return user_message

        if recent_context.lower() in user_message.lower():
            return user_message

        return f"{user_message}\n\nNgữ cảnh trước đó: {recent_context}"

    def _resolve_major_ambiguity(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: str = "",
    ) -> Optional[Dict[str, str]]:
        """Phát hiện khi user nhắc tới nhiều major và yêu cầu làm rõ."""
        explicit_candidates = self._find_major_candidates_in_text(user_message)
        if len(explicit_candidates) >= 2:
            return {
                "major_a": explicit_candidates[0],
                "major_b": explicit_candidates[1],
            }

        if active_major:
            current_major = active_major
        else:
            current_major = self._extract_context_major(history, current_message=user_message)
        if not current_major:
            return None

        current_display = MAJOR_DISPLAY.get(current_major, current_major).lower()
        alias_hits = 0
        if any(token in self._normalize_input(user_message) for token in ["ngành này", "ngành đó", "ngành ấy", "ngành kia", "nó", "đó", "này"]):
            alias_hits += 1
        if current_display and current_display in self._normalize_input(user_message):
            return None

        # Nếu câu mơ hồ nhắc tới ngành hiện tại nhưng chưa đủ rõ, chỉ hỏi lại khi có khả năng lẫn với major khác.
        if alias_hits > 0:
            for other in self.major_names:
                if other == current_major:
                    continue
                other_display = MAJOR_DISPLAY.get(other, other).lower()
                if other_display and other_display in self._normalize_input(user_message):
                    return {
                        "major_a": current_major,
                        "major_b": other,
                    }

        return None

    def chat(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        active_major: Optional[str] = None,
        active_topic: Optional[str] = None,
        feedback_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not user_message or not user_message.strip():
            return {
                "reply": "Bạn chưa nhập gì! Hãy hỏi mình về các ngành học hoặc gõ 'help' để được hướng dẫn.",
                "source": "system",
                "confidence": 1.0,
                "resolved_major": active_major or "",
                "resolved_topic": active_topic or "",
            }

        user_message = user_message.strip()

        if self._is_off_topic_personal(user_message):
            return {
                "reply": self._make_response_concise(self._build_scope_guard_reply()),
                "source": "scope_guard",
                "confidence": 0.99,
                "resolved_major": active_major or "",
                "resolved_topic": active_topic or "",
                "needs_clarification": False,
            }

        contextual_message = self._build_contextual_message(user_message, history)
        explicit_major = self._find_major_in_text(user_message)
        context_major = explicit_major or active_major or self._extract_context_major(history, current_message=user_message)
        followup_topic = self._detect_followup_topic(user_message) or (active_topic or "")

        ambiguity = None
        if not (explicit_major and self._is_major_selection_reply(user_message, explicit_major)):
            ambiguity = self._resolve_major_ambiguity(user_message, history=history, active_major=context_major)
        if ambiguity:
            major_a = ambiguity["major_a"]
            major_b = ambiguity["major_b"]
            return {
                "reply": self._build_ambiguity_clarification(major_a, major_b),
                "source": "context_clarify",
                "confidence": 0.35,
                "resolved_major": "",
                "resolved_topic": followup_topic or "overview",
                "needs_clarification": True,
                "clarify_options": [major_a, major_b],
            }

        if followup_topic and self._is_followup_question(user_message):
            if context_major:
                return {
                    "reply": self._make_response_concise(
                        self._build_contextual_followup_reply(followup_topic, context_major, feedback_data=feedback_data)
                    ),
                    "source": "context_followup",
                    "confidence": 0.98,
                    "resolved_major": context_major,
                    "resolved_topic": followup_topic,
                    "needs_clarification": False,
                }
            return {
                "reply": (
                    "Mình chưa xác định rõ ngành bạn đang nhắc tới. "
                    "Bạn có thể nói tên ngành cụ thể, hoặc gửi lại câu trước để mình trả lời chính xác hơn."
                ),
                "source": "context_clarify",
                "confidence": 0.2,
                "resolved_major": "",
                "resolved_topic": followup_topic,
                "needs_clarification": True,
            }

        if followup_topic and context_major and self._is_major_selection_reply(user_message, context_major):
            return {
                "reply": self._make_response_concise(
                    self._build_contextual_followup_reply(followup_topic, context_major, feedback_data=feedback_data)
                ),
                "source": "context_followup",
                "confidence": 0.97,
                "resolved_major": context_major,
                "resolved_topic": followup_topic,
                "needs_clarification": False,
            }

        if explicit_major:
            major_info = self.major_lookup.get(explicit_major, {})
            major_desc = major_info.get("mo_ta", "")
            return {
                "reply": self._build_major_bullet_reply(explicit_major, major_desc),
                "source": "explicit_major",
                "confidence": 0.92,
                "resolved_major": explicit_major,
                "resolved_topic": "overview",
                "needs_clarification": False,
            }

        greeting_resp = self._is_greeting(user_message)
        if greeting_resp:
            return {
                "reply": self._make_response_concise(greeting_resp),
                "source": "greeting",
                "confidence": 1.0,
                "resolved_major": context_major or "",
                "resolved_topic": followup_topic or "",
                "needs_clarification": False,
            }

        pattern_resp = self._check_pattern_match(contextual_message)
        if pattern_resp:
            return {
                "reply": self._make_response_concise(pattern_resp),
                "source": "pattern",
                "confidence": 0.95,
                "resolved_major": context_major or "",
                "resolved_topic": followup_topic or "overview",
                "needs_clarification": False,
            }

        tfidf_resp, confidence = self._get_tfidf_response(contextual_message)
        if tfidf_resp:
            resolved_major = explicit_major or self._find_major_in_text(tfidf_resp) or context_major or ""
            return {
                "reply": self._make_response_concise(tfidf_resp),
                "source": "model",
                "confidence": round(confidence, 2),
                "resolved_major": resolved_major,
                "resolved_topic": followup_topic or "overview",
                "needs_clarification": False,
            }

        fallback_resp = self._get_fallback_response(
            contextual_message,
            history=history,
            active_major=context_major or "",
            active_topic=followup_topic or "",
        )
        return {
            "reply": self._make_response_concise(fallback_resp),
            "source": "fallback",
            "confidence": 0.0,
            "resolved_major": context_major or "",
            "resolved_topic": followup_topic or "overview",
            "needs_clarification": False,
        }

    def get_major_info(self, major_key: str) -> Optional[Dict[str, str]]:
        """Get information about a specific major."""
        return self.major_lookup.get(major_key, None)

    def list_all_majors(self) -> List[str]:
        """Return list of all available majors."""
        return self.major_names
