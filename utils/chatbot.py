"""
Chatbot module for major recommendation system.
Uses model-based TF-IDF matching and fallback to external API if needed.
"""

from __future__ import annotations

import difflib
import json
import logging
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sklearn.metrics.pairwise import cosine_similarity

from .claude_fallback_api import get_claude_fallback_api
from .constants import BASE_DIR, MAJOR_DISPLAY, SUGGESTION_VI

MAJOR_EXTRA_ALIAS_MAP = {
    "Cong nghe thong tin": ["cntt", "it", "information technology", "cong nghe thong tin"],
}

MARINE_ALIAS_MAP = {
    "Dieu khien va quan ly tau bien": [
        "dieu khien va quan ly tau bien",
        "quan ly tau bien",
        "dieu khien tau bien",
        "lai tau",
        "lai tau",
        "hang hai",
        "nganh hang hai",
        "tau bien",
        "tau thuy",
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
        "quan ly hang hai",
        "si quan hang hai",
        "si quan boong",
        "deck officer",
        "ship officer",
        "seafaring",
        "vessel navigation",
        "ship handling",
        "vessel handling",
        "van tai bien",
        "quan ly van hanh tau bien",
    ],
    "Khai thac may tau thuy va quan ly ky thuat": [
        "khai thac may tau thuy va quan ly ky thuat",
        "khai thac may tau thuy va quan ly ky thuat",
        "khai thac may tau thuy",
        "quan ly ky thuat tau thuy",
        "may tau thuy",
        "may tau",
        "nganh may tau thuy",
        "nganh khai thac may tau thuy",
        "nganh quan ly ky thuat tau thuy",
        "thuyen may",
        "si quan may tau",
        "may truong",
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
        "hang hai ky thuat",
        "co dien tau thuy",
        "ky thuat tau thuy",
        "ky thuat may tau",
        "quan ly may tau",
        "bao tri may tau thuy",
        "sua chua may tau thuy",
    ],
}

# NEW: Keyword-to-Major mapping for sports/activities not in training data
SPORTS_KEYWORD_MAJOR_MAP = {
    "the thao": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "cau long": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "bong": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "bong da": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "bong chuyen": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "volleyball": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "tennis": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "co vua": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "the duc": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "huấn luyện viên": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "coach": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "the hanh": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "rut chi": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "dang buoc giay": ["Su pham Giao duc the chat", "Quan ly the thao"],
    "thi dau": ["Su pham Giao duc the chat", "Quan ly the thao"],
}

CUSTOM_MAJOR_ALIAS_MAP = {
    "Cong nghe thong tin": ["it", "cntt", "information technology", "computer science", "software", "software engineering"],
    "Ky thuat phan mem": ["software engineering", "software developer", "lap trinh phan mem"],
    "Khoa hoc du lieu": ["data science", "data scientist", "phan tich du lieu", "machine learning", "hoc may", "big data"],
    "Tri tue nhan tao": ["ai", "artificial intelligence", "machine learning", "deep learning"],
    "An ninh mang": ["cyber security", "cybersecurity", "network security", "bao mat mang"],
    "He thong thong tin": ["information systems", "mis", "business information systems"],
    "Ky thuat may tinh": ["computer engineering", "embedded systems", "hardware", "vi dieu khien"],
    "Ky thuat dien dien tu": ["electronics", "electrical engineering", "electricity", "dien tu"],
    "Tu dong hoa": ["automation", "control engineering", "plc", "scada"],
    "Ky thuat co khi": ["mechanical engineering", "co khi", "engineer"],
    "Ky thuat o to": ["automotive engineering", "oto", "car engineering"],
    "Ky thuat xay dung": ["civil engineering", "construction", "xay dung"],
    "Quan tri kinh doanh": ["business administration", "management", "business management"],
    "Marketing": ["digital marketing", "marketing management", "brand marketing"],
    "Thuong mai dien tu": ["e-commerce", "commerce", "tmdт", "thuong mai dien tu"],
    "Tai chinh ngan hang": ["finance", "banking", "financial management", "tai chinh"],
    "Ke toan": ["accounting", "ketoan"],
    "Kiem toan": ["auditing", "audit"],
    "Logistics va quan ly chuoi cung ung": ["logistics", "supply chain", "chuoi cung ung"],
    "Quan tri nhan luc": ["human resources", "hr", "nhan su"],
    "Kinh doanh quoc te": ["international business", "global business"],
    "Quan tri khach san": ["hospitality management", "hotel management"],
    "Quan tri nha hang va dich vu an uong": ["restaurant management", "food and beverage", "f&b"],
    "Khoi nghiep va doi moi sang tao": ["startup", "innovation", "khoi nghiep", "doi moi sang tao"],
    "Ngon ngu Anh": ["english", "tieng anh", "english language"],
    "Ngon ngu Trung": ["chinese", "mandarin", "tieng trung"],
    "Ngon ngu Nhat": ["japanese", "nihongo", "tieng nhat"],
    "Ngon ngu Han": ["korean", "hangul", "tieng han"],
    "Bao chi": ["journalism", "reporting"],
    "Truyen thong da phuong tien": ["multimedia", "media", "digital media"],
    "Quan he cong chung": ["pr", "public relations", "communications"],
    "Luat": ["law", "legal studies"],
    "Luat kinh te": ["business law", "commercial law"],
    "Tam ly hoc": ["psychology", "tam ly"],
    "Cong tac xa hoi": ["social work"],
    "Su pham Toan hoc": ["teacher training", "pedagogy", "su pham toan"],
    "Su pham Tin hoc": ["teacher training informatics", "informatics education", "su pham tin", "su pham tin hoc"],
    "Su pham Sinh hoc": ["teacher training biology", "biology education", "su pham sinh", "su pham sinh hoc"],
    "Su pham Hoa hoc": ["teacher training chemistry", "chemistry education", "su pham hoa", "su pham hoa hoc"],
    "Su pham Vat ly": ["teacher training physics", "physics education", "su pham ly", "su pham vat ly"],
    "Y da khoa": ["medicine", "medical doctor", "bac si"],
    "Duoc hoc": ["pharmacy", "duoc"],
    "Dieu duong": ["nursing", "dieu duong"],
    "Ky thuat xet nghiem y hoc": ["medical laboratory", "lab science"],
    "Ky thuat hinh anh y hoc": ["medical imaging", "radiology"],
    "Y hoc co truyen": ["traditional medicine"],
    "Rang ham mat": ["dentistry", "dental"],
    "Dinh duong": ["nutrition", "dinh duong"],
    "Y te cong cong": ["public health"],
    "Ho sinh": ["midwifery"],
    "Vat ly tri lieu va phuc hoi chuc nang": ["physiotherapy", "rehabilitation", "phuc hoi chuc nang"],
    "Thiet ke do hoa": ["graphic design", "ui ux", "ui/ux"],
    "Thiet ke thoi trang": ["fashion design"],
    "Thiet ke noi that": ["interior design"],
    "Kien truc": ["architecture"],
    "My thuat": ["fine arts", "art"],
    "Nhiep anh": ["nhiep anh", "photography"],
    "Quay phim - Dung phim": ["filmmaking", "video editing", "cinematography"],
    "Du lich": ["tourism", "travel", "boi loi", "boi loi", "the thao", "the thao", "bong", "bong", "the duc", "the duc", "the hanh", "the hanh", "ngoai troi", "ngoai troi", "hoat dong", "hoat dong", "kham pha", "kham pha", "khiem tham", "khiem tham"],
    "Quan tri dich vu du lich va lu hanh": ["tour operator", "travel management"],
    "Huong dan du lich": ["tour guide", "guide"],
    "Thiet ke game": ["game design", "game development"],
    "Nghe thuat so": ["digital art", "motion graphics"],
    "Dieu khien va quan ly tau bien": ["maritime", "marine", "nautical", "ship management", "ship officer"],
    "Khai thac may tau thuy va quan ly ky thuat": ["marine engineering", "engine room", "engine officer", "ship engineering"],
    "Su pham Lich su": ["teacher training history", "history education"],
    "Su pham Dia ly": ["teacher training geography", "geography education"],
    "Dia ly hoc": ["geography", "physical geography"],
    "Khoa hoc moi truong": ["environmental science", "environmental studies"],
    "Cong nghe thuc pham": ["food technology", "food science"],
}
from .chiasegpu_fallback_api import get_chiasegpu_fallback_api
from .claude_fallback_api import get_claude_fallback_api
from .deepseek_fallback_api import get_deepseek_fallback_api
from .openai_fallback_api import (
    get_bottom_fallback_api,
    get_last_fallback_api,
    get_openai_fallback_api,
)
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
            "xin chào": "Xin chào! 👋 Để mình tư vấn ngành học sát với bạn hơn, bạn hãy gửi trước: \n• Mô tả bản thân (Sở thích, tính cách, kỹ năng)\n• Định hướng tương lai",
            "hi": "Chào bạn! 👋 Trước khi tư vấn ngành, bạn cho mình 2 ý này nhé: \n• Mô tả bản thân (Sở thích, tính cách, kỹ năng)\n• Định hướng tương lai",
            "hello": "Hello 👋 Mình sẽ tư vấn ngành phù hợp hơn nếu bạn gửi trước: \n• Mô tả bản thân (Sở thích, tính cách, kỹ năng)\n• Định hướng tương lai",
            "helo": "Xin chào! 👋 Bạn gửi giúp mình 2 ý để bắt đầu tư vấn ngành nhé: \n• Mô tả bản thân (Sở thích, tính cách, kỹ năng)\n• Định hướng tương lai",
        }

        self.qa_patterns = {
            "cong nghe": "💻 3 ngành nổi bật:\n1️⃣ Công nghệ thông tin\n2️⃣ Khoa học dữ liệu\n3️⃣ An ninh mạng\n\nHợp nếu bạn thích lập trình và logic.",
            "may tinh": "💻 3 ngành máy tính:\n1️⃣ Công nghệ thông tin\n2️⃣ Khoa học dữ liệu\n3️⃣ Kỹ thuật máy tính\n\nNhu cầu cao, cơ hội tốt.",
            "ky thuat": "⚙️ 3 ngành kỹ thuật:\n1️⃣ Cơ khí\n2️⃣ Điện - điện tử\n3️⃣ Xây dựng\n\nHợp nếu bạn thích thực hành và tư duy logic.",
            "kinh doanh": "💼 3 ngành kinh doanh:\n1️⃣ Quản trị kinh doanh\n2️⃣ Marketing\n3️⃣ Tài chính - ngân hàng\n\nPhù hợp nếu bạn mạnh giao tiếp và quản lý.",
            "ngon ngu": "🌍 3 ngành ngôn ngữ:\n1️⃣ Tiếng Anh\n2️⃣ Tiếng Trung\n3️⃣ Tiếng Nhật\n\nTốt cho giao tiếp và môi trường quốc tế.",
            "suc khoe": "🏥 3 ngành sức khỏe:\n1️⃣ Y dược\n2️⃣ Điều dưỡng\n3️⃣ Dinh dưỡng\n\nHợp nếu bạn thích chăm sóc con người.",
            "du lich": "✈️ 3 ngành du lịch:\n1️⃣ Quản lý du lịch\n2️⃣ Hướng dẫn du lịch\n3️⃣ Thiết kế tour\n\nHợp nếu bạn thích giao tiếp và khám phá.",
            "giao duc": "📚 3 ngành giáo dục:\n1️⃣ Sư phạm Toán học\n2️⃣ Sư phạm Tin học\n3️⃣ Sư phạm Hóa học\n\nPhù hợp nếu bạn thích dạy học.",
            "thiet ke": "🎨 3 ngành thiết kế:\n1️⃣ Thiết kế đồ họa\n2️⃣ Thiết kế thời trang\n3️⃣ Thiết kế nội thất\n\nHợp nếu bạn có óc sáng tạo và thẩm mỹ.",
            "the thao": "🏃 3 ngành thể thao:\n1️⃣ Sư phạm Giáo dục thể chất\n2️⃣ Quản lý thể thao\n3️⃣ Huấn luyện viên thể thao\n\nPhù hợp nếu bạn thích thi đấu, rèn luyện sức khỏe.",
            "thi dau": "🏃 3 ngành thể thao:\n1️⃣ Sư phạm Giáo dục thể chất\n2️⃣ Quản lý thể thao\n3️⃣ Huấn luyện viên thể thao\n\nPhù hợp nếu bạn thích thi đấu, rèn luyện sức khỏe.",
            "bong": "🏃 3 ngành thể thao:\n1️⃣ Sư phạm Giáo dục thể chất\n2️⃣ Quản lý thể thao\n3️⃣ Huấn luyện viên thể thao\n\nPhù hợp nếu bạn thích bóng, thi đấu.",
        }

    def _normalize_input(self, text: str) -> str:
        text = str(text or "").strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace("đ", "d")
        text = re.sub(r"\s+", " ", text)
        return text

    def _normalize_for_lookup(self, text: str) -> str:
        return re.sub(r"\s+", " ", self._normalize_input(text)).strip()

    def _normalize_alias_value(self, text: str) -> str:
        normalized = self._normalize_for_lookup(text)
        normalized = normalized.replace("&", " va ")
        normalized = normalized.replace("/", " ")
        normalized = normalized.replace("-", " ")
        normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
        return re.sub(r"\s+", " ", normalized).strip()

    def _generate_major_aliases(self, major_key: str) -> List[str]:
        aliases = {
            self._normalize_alias_value(major_key),
            self._normalize_alias_value(MAJOR_DISPLAY.get(major_key, major_key)),
        }
        aliases.update(self._normalize_alias_value(alias) for alias in MAJOR_EXTRA_ALIAS_MAP.get(major_key, []))
        aliases.update(self._normalize_alias_value(alias) for alias in MARINE_ALIAS_MAP.get(major_key, []))
        aliases.update(self._normalize_alias_value(alias) for alias in CUSTOM_MAJOR_ALIAS_MAP.get(major_key, []))
        return sorted([alias for alias in aliases if alias], key=len, reverse=True)

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
            # Tránh lặp kiểu: "Ngành X tập trung vào Ngành X ..."
            cleaned_desc = re.sub(
                rf"^\s*ngành\s+{re.escape(major_display)}\s*",
                "",
                cleaned_desc,
                flags=re.IGNORECASE,
            ).strip(" ,.;:-")

            # Nếu mô tả vẫn mở đầu bằng "Ngành ..." (khác format), bỏ tiền tố chung.
            cleaned_desc = re.sub(r"^\s*ngành\s+", "", cleaned_desc, flags=re.IGNORECASE).strip(" ,.;:-")

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
            normalized_greeting = self._normalize_input(greeting_key)
            if re.search(r"\b" + re.escape(normalized_greeting) + r"\b", norm_text):
                return response
        return None

    def _check_pattern_match(self, text: str) -> Optional[str]:
        norm_text = self._normalize_input(text)
        for pattern_key, response in self.qa_patterns.items():
            if self._normalize_input(pattern_key) in norm_text:
                return response
        return None

    def _is_off_topic_personal(self, text: str) -> bool:
        """Nhận diện câu hỏi ngoài phạm vi tư vấn ngành (tình cảm/cá nhân/ngoại hình)."""
        norm_text = self._normalize_input(text)
        if not norm_text:
            return False

        # Các cụm này thuộc ngữ cảnh tư vấn mức độ phù hợp/ngành học, không phải tình cảm.
        safe_context_patterns = [
            r"\bthich hop\b",
            r"\bphu hop\b",
            r"\bso thich\b",
            r"\bnang luc\b",
            r"\btinh cach\b",
            r"\bhuong noi\b",
            r"\bhuong ngoai\b",
        ]
        if any(re.search(pattern, norm_text) for pattern in safe_context_patterns):
            return False

        # Exclude hobby/interest patterns to avoid false positives with "thích" (like)
        # CRITICAL: Add "cau long" and other sports to prevent blocking legitimate major queries
        hobby_patterns = [
            r"\bthich\s+(?:thi dau|the thao|bong|game|lap trinh|hoc|mon|nganh|van hoc|toan|ly|hoa|sinh|dia|su)\b",
            r"\bthich\s+(?:doc sach|nghe nhac|choi game|tho|thua|lua|ve|duong|vui|an|duong duong|lang|dam|dau)\b",
            # Add specific sports that could be blocked by romance pattern
            r"\bcau long\b",
            r"\bbong da\b",
            r"\bbong ro\b",
            r"\bthe duc\b",
            r"\bthe hanh\b",
            r"\byoga\b",
            r"\bkarate\b",
            r"\btaekwondo\b",
            r"\bkung fu\b",
        ]
        if any(re.search(pattern, norm_text) for pattern in hobby_patterns):
            return False

        romance_patterns = [
            r"\bnguoi yeu\b",
            r"\bto tinh\b",
            r"\bcrush\b",
            r"\bhen ho\b",
            r"\btoi yeu\b",
            r"\byeu\s+(?:ban|anh|chi|em|ai|nguoi ay)\b",
            r"\bny\b",
            r"\bban gai\b",
            r"\bban trai\b",
            r"\btha thinh\b",
            r"\bthich\s+(?:ban|cau|anh|chi|em|ai|nguoi ay)\b",
            # Only match "tôi thích + person pronoun" (not generic words)
            r"\b(?:toi|em|anh|chi|minh)\s+thich\s+(?:ban|cau|anh|chi|em|ai|nguoi|dia|no)\b",
        ]
        appearance_patterns = [
            r"\bdep trai\b",
            r"\bxinh gai\b",
            r"\bxinh\b",
            r"\bdep khong\b",
            r"\bkieu toc\b",
            r"\bcat toc\b",
            r"\bmakeup\b",
            r"\btrang diem\b",
            r"\bphoi do\b",
            r"\boutfit\b",
            r"\bthoi trang\b",
        ]
        all_patterns = romance_patterns + appearance_patterns
        return any(re.search(pattern, norm_text) for pattern in all_patterns)

    def _is_personality_fit_question(self, text: str) -> bool:
        """Nhận diện câu hỏi về tính cách/năng lực có hợp với ngành hay không."""
        norm_text = self._normalize_input(text)
        if not norm_text:
            return False

        fit_signals = [
            r"\bphu hop khong\b",
            r"\bco hop khong\b",
            r"\bthich hop khong\b",
            r"\bco thich hop khong\b",
            r"\bhop khong\b",
            r"\bnen hoc khong\b",
            r"\bco nen hoc khong\b",
            r"\btheo duoc khong\b",
            r"\bco phu hop khong\b",
            r"\bco hoc duoc khong\b",
            r"\bhoc duoc khong\b",
        ]
        trait_signals = [
            r"\bhuong noi\b",
            r"\bhuong ngoai\b",
            r"\bit noi\b",
            r"\btram tinh\b",
            r"\bnang dong\b",
            r"\btinh nong\b",
            r"\bnong tinh\b",
            r"\bde nong\b",
            r"\bhay cau\b",
            r"\bcau gat\b",
            r"\bgiao tiep kem\b",
            r"\bso giao tiep\b",
            r"\bkhong gioi giao tiep\b",
            r"\bkhong tu tin\b",
            r"\bchiu ap luc kem\b",
            r"\bhiv\b",
            r"\bbenh\b",
            r"\bbenh ly\b",
            r"\bsuc khoe yeu\b",
            r"\bthe trang yeu\b",
            r"\bcan thi\b",
            r"\bviem gan\b",
            r"\btinh cach\b",
            r"\bso thich\b",
            r"\bnang luc\b",
        ]

        has_trait = any(re.search(pattern, norm_text) for pattern in trait_signals)
        has_fit_signal = any(re.search(pattern, norm_text) for pattern in fit_signals)
        return has_trait or (has_fit_signal and not self._is_off_topic_personal(text))

    def _rewrite_personality_fit_message(self, user_message: str, major_key: str) -> str:
        """Viết lại ngắn gọn để downstream xử lý theo đúng major + intent phù hợp."""
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        cleaned = str(user_message or "").strip().rstrip("?.!")
        if not cleaned:
            return f"Người dùng đang hỏi liệu tính cách của họ có phù hợp với ngành {major_display} hay không."
        return f"Xét về tính cách và mức độ phù hợp với ngành {major_display}: {cleaned}?"

    def _extract_personality_traits(self, text: str) -> List[str]:
        """Lấy các trait chính từ câu người dùng để phản hồi tự nhiên hơn."""
        norm_text = self._normalize_input(text)
        if not norm_text:
            return []

        trait_patterns = [
            (r"\bhuong noi\b", "hướng nội"),
            (r"\bhuong ngoai\b", "hướng ngoại"),
            (r"\bit noi\b", "ít nói"),
            (r"\btram tinh\b", "trầm tính"),
            (r"\bnang dong\b", "năng động"),
            (r"\btinh nong\b", "tính nóng"),
            (r"\bnong tinh\b", "nóng tính"),
            (r"\bde nong\b", "dễ nóng"),
            (r"\bhay cau\b", "hay cáu"),
            (r"\bcau gat\b", "cáu gắt"),
            (r"\bgiao tiep kem\b", "giao tiếp chưa mạnh"),
            (r"\bso giao tiep\b", "hơi ngại giao tiếp"),
            (r"\bkhong gioi giao tiep\b", "giao tiếp chưa mạnh"),
            (r"\bkhong tu tin\b", "chưa quá tự tin"),
            (r"\bchiu ap luc kem\b", "chịu áp lực chưa tốt"),
            (r"\bhiv\b", "bị HIV"),
            (r"\bbenh ly\b", "có bệnh lý cần lưu ý"),
            (r"\bsuc khoe yeu\b", "sức khỏe hơi yếu"),
            (r"\bthe trang yeu\b", "thể trạng hơi yếu"),
            (r"\bcan thi\b", "bị cận thị"),
            (r"\bviem gan\b", "bị viêm gan"),
        ]

        traits: List[str] = []
        for pattern, label in trait_patterns:
            if re.search(pattern, norm_text) and label not in traits:
                traits.append(label)
        return traits

    def _build_trait_aware_fit_reply(self, major_key: str, user_message: str) -> str:
        """Tạo câu trả lời đánh giá độ phù hợp dựa trên trait user vừa nêu."""
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        major_norm = self._normalize_for_lookup(major_display)
        traits = self._extract_personality_traits(user_message)
        trait_text = ", ".join(traits) if traits else "những điểm bạn vừa chia sẻ"

        if any(token in major_norm for token in ["tau", "hang hai", "tau thuy", "marine", "maritime"]):
            return (
                f"Nếu bạn {trait_text} thì vẫn có thể theo ngành {major_display}, nhưng bạn cần cân nhắc kỹ vì môi trường này khá đặc thù.\n"
                f"• Ngành hợp hơn với người có kỷ luật cao, chịu áp lực tốt và thích nghi được môi trường làm việc xa nhà hoặc trên biển.\n"
                f"• Nếu bạn thiên về sự ổn định, ít thích dịch chuyển hoặc dễ mệt khi áp lực cao, bạn sẽ cần rèn thêm bản lĩnh và sức bền.\n"
                f"• Nói ngắn gọn: không phải là không hợp, nhưng bạn nên xem mình có sẵn sàng với nhịp sống và điều kiện làm việc của ngành này không."
            )

        return (
            f"Nếu bạn {trait_text} thì vẫn có thể hợp với ngành {major_display}, chứ không phải cứ vậy là không theo được.\n"
            f"• Quan trọng nhất là bạn có hứng thú thật với lĩnh vực này và sẵn sàng rèn dần những kỹ năng còn yếu.\n"
            f"• Với ngành {major_display}, người hướng nội hoặc giao tiếp chưa mạnh vẫn học tốt nếu có tư duy tự học, tập trung và chịu làm việc nghiêm túc.\n"
            f"• Nếu muốn, mình có thể đánh giá kỹ hơn theo kiểu: trait của bạn hợp điểm nào và sẽ vướng điểm nào với ngành này."
        )

    def _build_personality_fit_clarification(self) -> str:
        return (
            "Bạn đang hỏi mức độ phù hợp với ngành nào vậy? Ví dụ bạn có thể hỏi: "
            "'Em hướng nội, có hợp ngành Marketing không?' hoặc 'Em ít nói, có hợp CNTT không?'"
        )

    def _build_score_clarification(self) -> str:
        return (
            "Mình hiểu bạn đang hỏi về mức điểm thi/điểm xét tuyển, nhưng chưa rõ bạn muốn hỏi theo ngành hay theo nhóm ngành. "
            "Bạn có thể hỏi kiểu: '22 điểm hợp ngành nào?' hoặc 'Ngành Marketing khoảng bao nhiêu điểm?'"
        )

    def _is_vague_major_choice_question(self, text: str) -> bool:
        """Nhận diện câu hỏi chọn ngành quá mơ hồ để hỏi lại thay vì đoán TF-IDF."""
        norm_text = self._normalize_input(text)
        if not norm_text:
            return False

        vague_patterns = [
            r"\bhoc nganh nao\b",
            r"\bnen hoc nganh nao\b",
            r"\bchon nganh nao\b",
            r"\bthi nganh nao\b",
            r"\bmuon thi.*nganh nao\b",
            r"\bthi dau.*nganh nao\b",
            r"\bdau.*nganh nao\b",
            r"\bhop nganh nao\b",
        ]

        # Nếu đã có ngữ cảnh cụ thể như tên ngành, điểm số hoặc trait rõ ràng thì không xem là mơ hồ.
        if self._find_major_in_text(norm_text):
            return False
        if self._mentions_admission_score(norm_text):
            return False
        if self._is_personality_fit_question(norm_text):
            return False

        return any(re.search(pattern, norm_text) for pattern in vague_patterns)

    def _build_major_choice_clarification(self) -> str:
        return (
            "Mình hiểu bạn đang muốn hỏi nên học ngành nào, nhưng câu này chưa đủ thông tin để mình tư vấn chính xác. "
            "Bạn có thể nói thêm 1 trong 3 hướng sau: mức điểm hiện tại, nhóm sở thích/thế mạnh, hoặc tên ngành bạn đang phân vân. "
            "Ví dụ: 'Em được 22 điểm, hợp ngành nào?' hoặc 'Em thích công nghệ, nên học ngành nào?'"
        )

    def _mentions_admission_score(self, text: str) -> bool:
        norm_text = self._normalize_input(text)
        if not norm_text:
            return False

        score_patterns = [
            r"\bdiem thi\b",
            r"\bdiem em\b",
            r"\bdiem xet\b",
            r"\bdiem xet tuyen\b",
            r"\bdiem chuan\b",
            r"\bbao nhieu diem\b",
            r"\bmay diem\b",
            r"\btam \d+(?:[.,]\d+)?\s*d\b",
            r"\bmuc \d+(?:[.,]\d+)?\s*d\b",
            r"\bco \d+(?:[.,]\d+)?\s*d\b",
            r"\b\d+(?:[.,]\d+)?\s*diem\b",
            r"\b\d+(?:[.,]\d+)?\s*d\b",
        ]
        return any(re.search(pattern, norm_text) for pattern in score_patterns)

    def _build_scope_guard_reply(self) -> str:
        return (
            "Mình chuyên tư vấn ngành học và định hướng nghề nghiệp nên không phù hợp để tư vấn chuyện cá nhân như tình cảm hay ngoại hình. "
            "Bạn có thể hỏi mình về ngành phù hợp với sở thích/năng lực, học gì, học phí, cơ hội việc làm hoặc mức lương nhé."
        )

    def _build_major_suggestion_buttons(self, exclude_majors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Tạo gợi ý ngành dưới dạng nút bấm (3-5 ngành ngẫu nhiên)."""
        if exclude_majors is None:
            exclude_majors = []

        # Lọc ngành không bị exclude
        available_majors = [m for m in self.major_names if m not in exclude_majors]
        
        # Chọn ngẫu nhiên 3-5 ngành
        suggested_count = min(5, max(3, len(available_majors)))
        import random
        suggested_majors = random.sample(available_majors, suggested_count)
        
        return {
            "suggested_majors": suggested_majors,
            "major_displays": [MAJOR_DISPLAY.get(m, m) for m in suggested_majors],
            "buttons": [{"label": MAJOR_DISPLAY.get(m, m), "value": m} for m in suggested_majors],
        }

    def _build_clarification_question(self, question_type: str = "major") -> str:
        """Xây dựng câu hỏi làm rõ ngữ cảnh."""
        if question_type == "major":
            return "Bạn đang hỏi về ngành học nào? Hãy chọn hoặc gõ tên ngành nhé:"
        elif question_type == "topic":
            return "Bạn muốn biết về phần nào trong ngành này? Ví dụ:\n1️⃣ Học gì\n2️⃣ Chi phí học\n3️⃣ Cơ hội việc làm\n4️⃣ Điểm chuẩn"
        else:
            return "Mình chưa hiểu rõ. Bạn có thể nêu lại câu hỏi chi tiết hơn không?"

    def _should_ask_clarification(self, confidence: float, context_major: str, has_major_in_text: bool) -> bool:
        """Kiểm tra xem có nên hỏi lại người dùng không."""
        # Hỏi lại nếu: (confidence < 0.3 hoặc không tìm thấy ngành) và chưa hỏi quá 2 lần
        return (confidence < 0.3 or not has_major_in_text) and not context_major

    def _is_followup_question(self, text: str) -> bool:
        """Detect follow-up questions with pronoun resolution support."""
        norm_text = self._normalize_input(text)
        
        # Core follow-up patterns
        followup_patterns = [
            r"\bnganh nay\b",
            r"\bnganh do\b",
            r"\bnganh ay\b",
            r"\bnganh kia\b",
            r"\bnganh tren\b",
            r"\bluong\b",
            r"\bhoc phi\b",
            r"\bchi phi\b",
            r"\bcan tien\b",
            r"\bton tien\b",
            r"\bdiem thi\b",
            r"\bdiem em\b",
            r"\bdiem xet\b",
            r"\bdiem chuan\b",
            r"\bco hoi viec lam\b",
            r"\bdau ra\b",
            r"\bkho khong\b",
            r"\bco kho khong\b",
            r"\bphu hop khong\b",
            r"\bco phu hop khong\b",
            r"\bthich hop khong\b",
            r"\bco thich hop khong\b",
            r"\bhop khong\b",
            r"\bhuong noi\b",
            r"\bhuong ngoai\b",
            r"\bsuc khoe\b",
            r"\bthe luc\b",
            r"\bthe chat\b",
            r"\btinh nong\b",
            r"\bnong tinh\b",
            r"\bde nong\b",
            r"\bhay cau\b",
            r"\bcau gat\b",
            r"\btinh cach\b",
            r"\bthoi gian hoc\b",
            r"\bo dau\b",
            r"\bnen hoc\b",
            r"\bco nen\b",
            r"\bhoc gi\b",
            r"\bhoc nhung gi\b",
            r"\bmon gi\b",
            r"\byeu to nao\b",
            r"\bto chat\b",
            r"\bcan gi\b",
            r"\bphu hop voi ai\b",
        ]
        
        # Check explicit patterns
        if any(re.search(pattern, norm_text) for pattern in followup_patterns):
            return True
        
        # Pronoun resolution: detect pronouns without explicit major mention
        # These pronouns suggest follow-up questions: "nó", "cái đó", "ngành đó"
        pronoun_patterns = [
            r"\bno\b",      # it
            r"\bcai do\b",   # that one
            r"\bdia\b",      # it
            r"\bdau do\b",   # where
            r"\bnay\b",      # this (but less likely unless context exists)
            r"\bdo\b",       # that (but less likely unless context exists)
        ]
        if any(re.search(pattern, norm_text) for pattern in pronoun_patterns):
            # These alone suggest follow-up if no new major is mentioned
            return True
        
        # Check for admission score mentions
        return self._mentions_admission_score(text)

    def _find_major_in_text(self, text: str) -> str:
        """Find a major in text using exact match first, then fuzzy match."""
        norm_text = self._normalize_for_lookup(text)
        if not norm_text:
            return ""

        # Build candidates list
        candidates: List[Tuple[str, str]] = []
        for major_key in self.major_names:
            for alias in self._generate_major_aliases(major_key):
                candidates.append((major_key, alias))

        # Sort by length (longest first) to avoid partial matches
        sorted_candidates = sorted(candidates, key=lambda x: len(x[1]), reverse=True)
        
        # Try exact substring match first (most reliable)
        for major_key, major_name in sorted_candidates:
            if major_name and major_name in norm_text:
                return major_key
        
        # Fallback: Try fuzzy match with levenshtein-like logic for common typos
        import difflib
        for major_key, major_name in sorted_candidates:
            if not major_name:
                continue
            # Use SequenceMatcher for fuzzy matching (threshold 0.85)
            ratio = difflib.SequenceMatcher(None, major_name, norm_text).ratio()
            if ratio > 0.85:
                return major_key
        
        return ""

    def _find_major_candidates_in_text(self, text: str) -> List[str]:
        """Tìm tất cả major xuất hiện trong text theo thứ tự xuất hiện trong câu người dùng."""
        norm_text = self._normalize_for_lookup(text)
        if not norm_text:
            return []

        major_first_pos: Dict[str, int] = {}
        for major_key in self.major_names:
            aliases = self._generate_major_aliases(major_key)

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
        return self._generate_major_aliases(major_key)

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
        """Lấy ngành đang được nói tới gần nhất theo thứ tự tin nhắn gần nhất → cũ hơn.
        Enhanced to search deeper through history and find major from user's initial request."""
        current_major = self._find_major_in_text(current_message)
        if current_major:
            return current_major
        if not history:
            return ""

        current_norm = self._normalize_for_lookup(current_message)
        
        # Pass 1: Search recent history (20 messages) - most likely to have context
        recent_history = list(history)[-20:]
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
        
        # Pass 2: If not found in recent, search entire history
        # This catches cases where user asked about a major early in conversation
        entire_history = list(history)
        for item in reversed(entire_history):
            if not isinstance(item, dict):
                continue

            content = str(item.get("content", "")).strip()
            role = str(item.get("role", "")).strip()
            if not content:
                continue
            
            # Only check user messages for deeper context
            if role != "user":
                continue
                
            if current_norm and self._normalize_for_lookup(content) == current_norm:
                continue

            major_key = self._find_major_in_text(content)
            if major_key:
                logger.debug(f"Found context major from history: {major_key}")
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

    def _build_intelligent_context_summary(
        self, 
        history: Optional[List[Dict[str, Any]]], 
        max_messages: int = 10,
        max_chars: int = 500
    ) -> str:
        """Tạo tóm tắt ngữ cảnh thông minh - extract key info thay vì text cắt cắp."""
        if not history:
            return ""
        
        import re
        summary_parts: List[str] = []
        
        # Extract từ user messages gần nhất
        user_messages = [item for item in reversed(history[-max_messages:]) 
                        if isinstance(item, dict) and item.get("role") == "user"]
        
        for msg in user_messages[:5]:  # Tối đa 5 tin nhắn gần nhất
            content = str(msg.get("content", "")).strip()
            if not content or len(content) > max_chars:
                continue
            
            # Extract key phrases - major names, topics, traits
            major_keywords = self._find_major_candidates_in_text(content)
            if major_keywords:
                major_displays = [MAJOR_DISPLAY.get(m, m) for m in major_keywords[:2]]
                summary_parts.append(f"Nhắc tới ngành: {', '.join(major_displays)}")
            
            # Extract topic
            topic = self._detect_followup_topic(content)
            if topic:
                topic_map = {
                    "admission_score": "Hỏi về điểm xét tuyển",
                    "salary": "Hỏi về mức lương",
                    "difficulty": "Hỏi về độ khó",
                    "career": "Hỏi về cơ hội việc làm",
                    "study_content": "Hỏi học gì",
                    "fit_factors": "Hỏi về phù hợp"
                }
                summary_parts.append(f"Chủ đề: {topic_map.get(topic, topic)}")
        
        return " | ".join(summary_parts[:3]) if summary_parts else ""

    def _score_response_quality(self, response: str, question: str, context_major: str = "") -> float:
        """Tính điểm chất lượng phản hồi (0-1). Cao = phản hồi tốt."""
        if not response:
            return 0.0
        
        score = 0.5  # Baseline
        
        # Bonus points
        if len(response) > 80:  # Phản hồi đủ chi tiết
            score += 0.15
        if len(response) < 500:  # Nhưng không quá dài
            score += 0.05
        if "\n" in response or "•" in response or ":" in response:  # Có cấu trúc
            score += 0.15
        if context_major and any(kw in response.lower() for kw in ["ngành", "học", "kỹ năng", "cơ hội"]):
            score += 0.1
        if re.search(r"[0-9]{1,2}\s*(triệu|năm|%)", response):  # Có dữ liệu cụ thể
            score += 0.1
        
        # Penalty points
        if response.count("...") > 2:  # Quá nhiều ellipsis
            score -= 0.15
        if len(response.split()) < 20:  # Quá ngắn
            score -= 0.2
        
        return max(0.0, min(1.0, score))

    def _build_context_aware_system_prompt(
        self,
        question: str,
        chat_turn: int,
        question_type: str = "general"
    ) -> str:
        """Xây dựng system prompt tối ưu - ngắn gọn & focus."""
        
        # COMPACT PERSONA - giữ chỉ điều cần thiết
        persona = "Bạn là trợ lý tư vấn ngành học chuyên nghiệp."
        
        # TONE MAPPING - tập trung vào hành động
        tone_by_type = {
            "greeting": "Chào hỏi ấm áp. Hỏi lại để hiểu nhu cầu.",
            "personality_fit": "Chi tiết về yếu tố tính cách + liên hệ ngành.",
            "salary": "Cung cấp dữ liệu cụ thể hoặc ước lượng.",
            "career": "Nêu con đường sự nghiệp & vị trí cụ thể.",
            "difficulty": "Đánh giá thực tế + cách chuẩn bị.",
            "general": "Trả lời 80-150 từ, chính xác, cụ thể."
        }
        
        selected_tone = tone_by_type.get(question_type, tone_by_type["general"])
        
        # ANTI-REPETITION - chỉ thêm khi cần thiết
        if chat_turn > 3:
            selected_tone += " Diễn đạt khác lần trước."
        
        # MINIMAL PROMPT - loại bỏ dư thừa
        instructions = f"{persona}\n{selected_tone}"
        return instructions.strip()

    def _validate_and_regenerate_response(
        self, 
        response: str,
        question: str,
        api_func,
        context_major: str = "",
        history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Kiểm tra chất lượng phản hồi, nếu thấp thì regenerate."""
        quality_score = self._score_response_quality(response, question, context_major)
        
        # Nếu chất lượng tốt (>0.6) thì return luôn
        if quality_score >= 0.6:
            return response
        
        # Quality thấp - cần cải thiện
        logger.warning(f"Low quality response (score: {quality_score:.2f}), attempting to regenerate...")
        
        # Thử gọi API với prompt tốt hơn
        try:
            improved_prompt = f"""Phản hồi trước của bạn chưa đủ chi tiết. 
Bạn vui lòng trả lời lại câu này một cách chi tiết hơn, cụ thể hơn, và toàn diện hơn:

Câu hỏi: {question}

Hãy trả lời với:
- Chi tiết cụ thể (nếu có dữ liệu)
- Ví dụ thực tế
- Hướng dẫn hành động
- Lợi ích/thách thức
"""
            
            better_response = api_func(improved_prompt)
            if better_response:
                new_quality = self._score_response_quality(better_response, question, context_major)
                if new_quality > quality_score:
                    logger.info(f"Regenerated response with better quality: {new_quality:.2f}")
                    return better_response
        except Exception as e:
            logger.warning(f"Regeneration failed: {e}")
        
        # Nếu regeneration fail hoặc ko tốt hơn, return original
        return response

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
        if self._is_personality_fit_question(user_message):
            return "fit_factors"
        if self._mentions_admission_score(user_message):
            return "admission_score"
        if any(key in norm_text for key in ["luong", "thu nhap", "tien luong"]):
            return "salary"
        if any(key in norm_text for key in ["co kho khong", "do kho", "kho khan"]):
            return "difficulty"
        if any(key in norm_text for key in ["hoc phi", "chi phi", "can tien", "ton tien", "dat", "dat khong"]):
            return "tuition"
        if any(key in norm_text for key in ["viec lam", "dau ra", "co hoi viec lam"]):
            return "career"
        if any(key in norm_text for key in ["thoi gian hoc", "may nam", "bao lau"]):
            return "duration"
        if any(key in norm_text for key in ["hoc gi", "hoc nhung gi", "mon gi", "hoc mon gi"]):
            return "study_content"
        if any(key in norm_text for key in ["suc khoe", "the luc", "the chat"]):
            return "fit_factors"
        if any(key in norm_text for key in ["hiv", "benh", "benh ly", "suc khoe yeu", "the trang yeu", "can thi", "viem gan"]):
            return "fit_factors"
        if any(key in norm_text for key in ["yeu to nao", "to chat", "can gi", "phu hop voi ai", "nang luc nao"]):
            return "fit_factors"
        if any(key in norm_text for key in ["nganh do", "nganh nay", "nganh ay", "nganh kia", "biet them", "them gi"]):
            return "overview"
        return ""

    def _build_contextual_followup_reply(
        self,
        topic: str,
        major_key: str,
        feedback_data: Optional[Dict[str, Any]] = None,
        user_message: str = "",
    ) -> str:
        import random
        major_display = MAJOR_DISPLAY.get(major_key, major_key)
        major_info = self.major_lookup.get(major_key, {})
        major_desc = str(major_info.get("mo_ta", "")).strip()
        source_numeric_fact = self._extract_source_numeric_fact(major_key, feedback_data=feedback_data)

        if topic == "admission_score":
            admission_variants = [
                f"Với ngành {major_display}, mức điểm xét tuyển thay đổi theo từng trường, từng năm và phương thức xét tuyển.\n• Nếu bạn có tên trường hoặc tổ hợp xét tuyển, mình có thể giúp bạn định hướng sát hơn.\n• Nếu bạn chỉ đang hỏi theo mức điểm hiện có, mình cũng có thể gợi ý nhóm ngành/trường ở khoảng điểm đó.",
                f"Điểm xét tuyển của ngành {major_display} không cố định - nó tùy vào trường và năm tuyển sinh. Bạn có thể cung cấp tên trường hoặc tổ hợp môn để mình tư vấn chính xác hơn.",
                f"Để chính xác về điểm xét tuyển ngành {major_display}, bạn nên kiểm tra với từng trường cụ thể vì điểm thay đổi hàng năm. Nếu bạn nêu điểm hiện có, mình có thể giúp tìm trường phù hợp.",
            ]
            return random.choice(admission_variants)
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
            if self._is_personality_fit_question(user_message):
                return self._build_trait_aware_fit_reply(major_key, user_message)

            major_norm = self._normalize_for_lookup(major_display)
            if any(token in major_norm for token in ["tau", "hang hai", "tau thuy", "marine", "maritime"]):
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

    def _compare_model_vs_fallback(self, tfidf_resp: str, fallback_resp: str, user_message: str) -> bool:
        """Compare TF-IDF vs fallback response. Returns True if fallback is better."""
        norm_msg = self._normalize_input(user_message)
        
        # Extract mentioned majors from user message
        mentioned_majors = self._find_major_candidates_in_text(user_message)
        
        # If user mentions multiple majors, fallback should handle it better
        if len(mentioned_majors) >= 2:
            # Check if fallback mentions multiple majors
            fallback_norm = self._normalize_input(fallback_resp)
            major_count_in_fallback = sum(1 for major in mentioned_majors 
                                         if self._normalize_input(MAJOR_DISPLAY.get(major, major)) in fallback_norm)
            
            # If fallback covers more majors than TF-IDF, it's better
            if major_count_in_fallback > 1:
                return True
        
        # If TF-IDF response is generic template, fallback is likely better
        if "💡 Phù hợp nếu bạn thích ngành này" in tfidf_resp and len(fallback_resp) > len(tfidf_resp) * 1.5:
            return True
        
        return False

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
        """Get fallback response from external APIs with intelligent context awareness."""
        import random
        
        # FIX: Use text directly for API call, not context packet
        # This ensures each question gets its own response, not cached from previous questions
        fallback_input = self._build_context_packet(
            user_message=text,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
        )
        
        # API chain with timeout attempts
        api_chain = [
            ("Deepseek", get_deepseek_fallback_api, 5),
            ("OpenAI", get_openai_fallback_api, 5),
            ("Claude", get_claude_fallback_api, 5),
            ("ChiaSeGPU", get_chiasegpu_fallback_api, 5),
            ("Last Fallback", get_last_fallback_api, 5),
            ("Bottom Fallback", get_bottom_fallback_api, 5),
        ]
        
        for api_name, api_factory, timeout_secs in api_chain:
            try:
                api = api_factory()
                # FIX: Pass text directly to API, not the context packet
                # This ensures cache key is based on actual question, not context
                logger.debug(f"🔄 Calling {api_name} API with user question: '{text[:50]}...'")
                result = api.analyze_free_text(
                    text,  # FIX: Use text (actual question) instead of fallback_input
                    context="chatbot",
                    history=history,
                    active_major=active_major,
                    active_topic=active_topic,
                )

                if isinstance(result, dict) and result.get("success"):
                    response_text = str(result.get("response", "")).strip()
                    if response_text and len(response_text) > 20:  # Ensure response is substantial
                        logger.info(f"✅ {api_name} returned response ({len(response_text)} chars)")
                        response_text = self._limit_to_top3_majors(response_text)
                        # Keep more content, be less aggressive with sanitization
                        return self._make_response_concise(response_text)
                    else:
                        logger.warning(f"⚠️ {api_name} returned empty/short response, trying next API")
                        continue
            except TimeoutError as exc:
                logger.warning(f"{api_name} API timeout: {exc}")
                continue
            except Exception as exc:
                logger.warning(f"{api_name} API failed: {exc}")
                continue
        
        # All APIs failed - provide better fallback response
        better_fallback = (
            f"Mình chưa hiểu rõ câu hỏi của bạn: '{text}'.\n\n"
            f"Bạn có thể thử:\n"
            f"• Hỏi về 1 ngành cụ thể (ví dụ: 'Công nghệ thông tin có gì hay?')\n"
            f"• Điền form để nhận gợi ý chính xác hơn\n"
            f"• Nêu sở thích/kỹ năng của bạn để mình tư vấn\n"
            f"• Tiếp tục chat để mình hỗ trợ thêm"
        )
        return self._make_response_concise(better_fallback)

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

    def _detect_sports_keyword(self, user_message: str) -> Optional[str]:
        """
        NEW: Detect sports-related keywords and return recommended major.
        Returns the first matching sports major key, or None if no sports keyword detected.
        """
        norm_text = self._normalize_input(user_message)
        for keyword, major_list in SPORTS_KEYWORD_MAJOR_MAP.items():
            if keyword in norm_text:
                # Return the first (preferred) major for this sport
                return major_list[0]
        return None

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
        if any(token in self._normalize_input(user_message) for token in ["nganh nay", "nganh do", "nganh ay", "nganh kia", "no", "do", "nay"]):
            alias_hits += 1
        normalized_current_display = self._normalize_input(current_display)
        if normalized_current_display and normalized_current_display in self._normalize_input(user_message):
            return None

        # Nếu câu mơ hồ nhắc tới ngành hiện tại nhưng chưa đủ rõ, chỉ hỏi lại khi có khả năng lẫn với major khác.
        if alias_hits > 0:
            for other in self.major_names:
                if other == current_major:
                    continue
                other_display = self._normalize_input(MAJOR_DISPLAY.get(other, other).lower())
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

        # NEW: Check for sports keyword first (before model inference)
        sports_major = self._detect_sports_keyword(user_message)
        if sports_major:
            major_display = MAJOR_DISPLAY.get(sports_major, sports_major)
            sports_response = (
                f"🏃 **{major_display}**\n\n"
                f"Mình nhận thấy bạn thích thể thao! Đây là những ngành học rất phù hợp:\n\n"
                f"• **{major_display}** - Nếu bạn muốn trở thành giáo viên, huấn luyện viên hoặc chuyên gia thể thao.\n"
                f"• Bạn sẽ học về sinh lý thể thao, kỹ thuật huấn luyện, tâm lý thi đấu.\n"
                f"• Cơ hội việc làm: Trường học, câu lạc bộ, đội tuyển, trung tâm thể thao.\n\n"
                f"Bạn muốn biết thêm về ngành này không? Hoặc tôi có thể giới thiệu ngành liên quan khác."
            )
            return {
                "reply": self._make_response_concise(sports_response),
                "source": "sports_keyword",
                "confidence": 0.95,
                "resolved_major": sports_major,
                "resolved_topic": "sports_recommendation",
                "needs_clarification": False,
            }

        explicit_major = self._find_major_in_text(user_message)
        context_major = explicit_major or active_major or self._extract_context_major(history, current_message=user_message)
        personality_fit_question = self._is_personality_fit_question(user_message)
        score_question = self._mentions_admission_score(user_message)
        vague_major_choice_question = self._is_vague_major_choice_question(user_message)

        if personality_fit_question and not context_major:
            return {
                "reply": self._build_personality_fit_clarification(),
                "source": "context_clarify",
                "confidence": 0.3,
                "resolved_major": "",
                "resolved_topic": "fit_factors",
                "needs_clarification": True,
            }

        if score_question and not context_major:
            return {
                "reply": self._build_score_clarification(),
                "source": "context_clarify",
                "confidence": 0.35,
                "resolved_major": "",
                "resolved_topic": "admission_score",
                "needs_clarification": True,
            }

        if vague_major_choice_question and not context_major:
            return {
                "reply": self._build_major_choice_clarification(),
                "source": "context_clarify",
                "confidence": 0.3,
                "resolved_major": "",
                "resolved_topic": "major_selection",
                "needs_clarification": True,
            }

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
        if personality_fit_question and context_major:
            contextual_message = self._rewrite_personality_fit_message(user_message, context_major)
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
                        self._build_contextual_followup_reply(
                            followup_topic,
                            context_major,
                            feedback_data=feedback_data,
                            user_message=user_message,
                        )
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
                    self._build_contextual_followup_reply(
                        followup_topic,
                        context_major,
                        feedback_data=feedback_data,
                        user_message=user_message,
                    )
                ),
                "source": "context_followup",
                "confidence": 0.97,
                "resolved_major": context_major,
                "resolved_topic": followup_topic,
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

        # NEW: Detect off-topic queries (input không liên quan đến ngành)
        # Nếu input không có major nào được nhắc tới → force fallback
        is_off_topic = (
            not explicit_major 
            and not context_major 
            and not followup_topic 
            and not personality_fit_question 
            and not score_question
            and not vague_major_choice_question
        )

        tfidf_resp, confidence = self._get_tfidf_response(contextual_message)
        
        # HYBRID LOGIC: If off-topic → use fallback only (không dùng model)
        if is_off_topic:
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
        
        # HYBRID LOGIC: High confidence (>= 0.85) → use model
        if tfidf_resp and confidence >= 0.85:
            resolved_major = explicit_major or self._find_major_in_text(tfidf_resp) or context_major or ""
            return {
                "reply": self._make_response_concise(tfidf_resp),
                "source": "model",
                "confidence": round(confidence, 2),
                "resolved_major": resolved_major,
                "resolved_topic": followup_topic or "overview",
                "needs_clarification": False,
            }
        
        # HYBRID LOGIC: Medium confidence (0.75-0.85) → verify with fallback
        if tfidf_resp and 0.75 <= confidence < 0.85:
            fallback_resp = self._get_fallback_response(
                contextual_message,
                history=history,
                active_major=context_major or "",
                active_topic=followup_topic or "",
            )
            
            # Compare and choose better response
            if self._compare_model_vs_fallback(tfidf_resp, fallback_resp, user_message):
                # Fallback is better
                resolved_major = context_major or ""
                return {
                    "reply": self._make_response_concise(fallback_resp),
                    "source": "fallback_verified",
                    "confidence": round(confidence, 2),
                    "resolved_major": resolved_major,
                    "resolved_topic": followup_topic or "overview",
                    "needs_clarification": False,
                }
            else:
                # Model is better
                resolved_major = explicit_major or self._find_major_in_text(tfidf_resp) or context_major or ""
                return {
                    "reply": self._make_response_concise(tfidf_resp),
                    "source": "model_verified",
                    "confidence": round(confidence, 2),
                    "resolved_major": resolved_major,
                    "resolved_topic": followup_topic or "overview",
                    "needs_clarification": False,
                }
        
        # HYBRID LOGIC: Low confidence (< 0.75) → use fallback only
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
