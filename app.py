import json
import logging
import os
import random
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request, session

from utils.chatbot import MajorChatbot
from utils.chiasegpu_fallback_api import get_chiasegpu_fallback_api
from utils.claude_fallback_api import get_claude_fallback_api
from utils.constants import CATEGORICAL_COLS, MAJOR_DISPLAY, SUGGESTION_VI
from utils.deepseek_fallback_api import get_deepseek_fallback_api
from utils.features import row_dict_from_payload
from utils.openai_fallback_api import (
    get_bottom_fallback_api,
    get_last_fallback_api,
    get_openai_fallback_api,
)
from utils.predictor import Predictor, load_predictor
from utils.response_validator import ResponseValidator

# FIX: Load major list at startup for fallback API constraint
@lru_cache(maxsize=1)
def load_major_list() -> list:
    """Load list of available majors from majors.json for fallback API constraint."""
    try:
        majors_path = BASE_DIR / "models" / "majors.json"
        if majors_path.exists():
            with open(majors_path, "r", encoding="utf-8") as f:
                majors_data = json.load(f)
                major_list = [m.get("nganh") for m in majors_data if isinstance(m, dict) and m.get("nganh")]
                logger.info(f"✓ Loaded {len(major_list)} majors for fallback API constraint")
                return major_list
    except Exception as e:
        logger.warning(f"⚠ Could not load major list: {e}")
    return []

MAJOR_GROUPS = {
    "An ninh mang": "Công nghệ - Kỹ thuật",
    "Bao chi": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Cong nghe thong tin": "Công nghệ - Kỹ thuật",
    "Cong nghe thuc pham": "Công nghệ - Kỹ thuật",
    "Cong tac xa hoi": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Dia ly hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Dieu duong": "Sức khỏe - Dịch vụ cộng đồng",
    "Dieu khien va quan ly tau bien": "Công nghệ - Kỹ thuật",
    "Dinh duong": "Sức khỏe - Dịch vụ cộng đồng",
    "Du lich": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Duoc hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "He thong thong tin": "Công nghệ - Kỹ thuật",
    "Ho sinh": "Sức khỏe - Dịch vụ cộng đồng",
    "Huong dan du lich": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Ke toan": "Kinh doanh - Tài chính - Quản trị",
    "Khai thac may tau thuy va quan ly ky thuat": "Công nghệ - Kỹ thuật",
    "Khoa hoc du lieu": "Công nghệ - Kỹ thuật",
    "Khoa hoc moi truong": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Khoi nghiep va doi moi sang tao": "Kinh doanh - Tài chính - Quản trị",
    "Kiem toan": "Kinh doanh - Tài chính - Quản trị",
    "Kien truc": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Kinh doanh quoc te": "Kinh doanh - Tài chính - Quản trị",
    "Ky thuat co khi": "Công nghệ - Kỹ thuật",
    "Ky thuat dien dien tu": "Công nghệ - Kỹ thuật",
    "Ky thuat hinh anh y hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Ky thuat may tinh": "Công nghệ - Kỹ thuật",
    "Ky thuat o to": "Công nghệ - Kỹ thuật",
    "Ky thuat phan mem": "Công nghệ - Kỹ thuật",
    "Ky thuat xay dung": "Công nghệ - Kỹ thuật",
    "Ky thuat xet nghiem y hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Logistics va quan ly chuoi cung ung": "Kinh doanh - Tài chính - Quản trị",
    "Luat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Luat kinh te": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Marketing": "Kinh doanh - Tài chính - Quản trị",
    "My thuat": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Nghe thuat so": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Ngon ngu Anh": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Han": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Nhat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Trung": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Nhiếp anh": "Công nghệ - Kỹ thuật",
    "Quan he cong chung": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Quan ly cang va logistics": "Kinh doanh - Tài chính - Quản trị",
    "Quan ly the thao": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Quan tri dich vu du lich va lu hanh": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Quan tri khach san": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri kinh doanh": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri nha hang va dich vu an uong": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri nhan luc": "Kinh doanh - Tài chính - Quản trị",
    "Quay phim - Dung phim": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Rang ham mat": "Sức khỏe - Dịch vụ cộng đồng",
    "Su pham Dia ly": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Giao duc the chat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Hoa hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Lich su": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Sinh hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Tin hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Toan hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Vat ly": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Tai chinh ngan hang": "Kinh doanh - Tài chính - Quản trị",
    "Tam ly hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Thiet ke do hoa": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke game": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke noi that": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke thoi trang": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thuong mai dien tu": "Kinh doanh - Tài chính - Quản trị",
    "Tri tue nhan tao": "Công nghệ - Kỹ thuật",
    "Truyen thong da phuong tien": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Tu dong hoa": "Công nghệ - Kỹ thuật",
    "Vat ly tri lieu va phuc hoi chuc nang": "Sức khỏe - Dịch vụ cộng đồng",
    "Y da khoa": "Sức khỏe - Dịch vụ cộng đồng",
    "Y hoc co truyen": "Sức khỏe - Dịch vụ cộng đồng",
    "Y te cong cong": "Sức khỏe - Dịch vụ cộng đồng",
}

SAMPLE_PROFILES = [
    {
        "so_thich_chinh": "Công nghệ",
        "mon_hoc_yeu_thich": "Tin học",
        "ky_nang_noi_bat": "Tư duy logic",
        "tinh_cach": "Kỷ luật",
        "moi_truong_lam_viec_mong_muon": "Kỹ thuật",
        "muc_tieu_nghe_nghiep": "Phát triển chuyên môn",
        "mo_ta_ban_than": "Em thích lập trình, tìm lỗi hệ thống và tối ưu hiệu năng.",
        "dinh_huong_tuong_lai": "Em muốn trở thành kỹ sư phần mềm hoặc kỹ sư AI.",
    },
    {
        "so_thich_chinh": "Công nghệ",
        "mon_hoc_yeu_thich": "Toán",
        "ky_nang_noi_bat": "Phân tích dữ liệu",
        "tinh_cach": "Tỉ mỉ",
        "moi_truong_lam_viec_mong_muon": "Văn phòng",
        "muc_tieu_nghe_nghiep": "Thu nhập cao",
        "mo_ta_ban_than": "Em yêu thích số liệu, biểu đồ và các bài toán phân tích.",
        "dinh_huong_tuong_lai": "Em muốn làm Data Analyst hoặc Data Scientist.",
    },
    {
        "so_thich_chinh": "Kinh doanh",
        "mon_hoc_yeu_thich": "Toán",
        "ky_nang_noi_bat": "Lãnh đạo",
        "tinh_cach": "Quyết đoán",
        "moi_truong_lam_viec_mong_muon": "Văn phòng",
        "muc_tieu_nghe_nghiep": "Khởi nghiệp",
        "mo_ta_ban_than": "Em thích xây dựng kế hoạch, quản lý đội nhóm và bán hàng.",
        "dinh_huong_tuong_lai": "Em muốn học quản trị để mở doanh nghiệp riêng.",
    },
    {
        "so_thich_chinh": "Kinh doanh",
        "mon_hoc_yeu_thich": "Anh",
        "ky_nang_noi_bat": "Giao tiếp",
        "tinh_cach": "Năng động",
        "moi_truong_lam_viec_mong_muon": "Linh hoạt",
        "muc_tieu_nghe_nghiep": "Trải nghiệm quốc tế",
        "mo_ta_ban_than": "Em thích làm việc với khách hàng và đàm phán hợp tác.",
        "dinh_huong_tuong_lai": "Em muốn theo ngành kinh doanh quốc tế hoặc marketing.",
    },
    {
        "so_thich_chinh": "Du lịch",
        "mon_hoc_yeu_thich": "Anh",
        "ky_nang_noi_bat": "Thuyết trình",
        "tinh_cach": "Hướng ngoại",
        "moi_truong_lam_viec_mong_muon": "Linh hoạt",
        "muc_tieu_nghe_nghiep": "Theo đam mê",
        "mo_ta_ban_than": "Em thích khám phá văn hóa và giới thiệu địa điểm mới cho mọi người.",
        "dinh_huong_tuong_lai": "Em muốn làm hướng dẫn viên hoặc điều hành tour.",
    },
    {
        "so_thich_chinh": "Du lịch",
        "mon_hoc_yeu_thich": "Văn",
        "ky_nang_noi_bat": "Tổ chức & lập kế hoạch",
        "tinh_cach": "Trách nhiệm",
        "moi_truong_lam_viec_mong_muon": "Văn phòng",
        "muc_tieu_nghe_nghiep": "Ổn định",
        "mo_ta_ban_than": "Em thích lên lịch trình chi tiết và chăm sóc trải nghiệm khách hàng.",
        "dinh_huong_tuong_lai": "Em muốn làm quản trị dịch vụ du lịch và lữ hành.",
    },
    {
        "so_thich_chinh": "Nghệ thuật",
        "mon_hoc_yeu_thich": "Văn",
        "ky_nang_noi_bat": "Sáng tạo",
        "tinh_cach": "Tỉ mỉ",
        "moi_truong_lam_viec_mong_muon": "Linh hoạt",
        "muc_tieu_nghe_nghiep": "Theo đam mê",
        "mo_ta_ban_than": "Em thích màu sắc, bố cục và thiết kế nội dung truyền thông.",
        "dinh_huong_tuong_lai": "Em muốn làm thiết kế đồ họa hoặc UI/UX.",
    },
    {
        "so_thich_chinh": "Nghệ thuật",
        "mon_hoc_yeu_thich": "Anh",
        "ky_nang_noi_bat": "Sáng tạo",
        "tinh_cach": "Hướng nội",
        "moi_truong_lam_viec_mong_muon": "Linh hoạt",
        "muc_tieu_nghe_nghiep": "Phát triển chuyên môn",
        "mo_ta_ban_than": "Em thích kể chuyện bằng hình ảnh và dựng video ngắn.",
        "dinh_huong_tuong_lai": "Em muốn theo ngành truyền thông đa phương tiện.",
    },
    {
        "so_thich_chinh": "Y tế",
        "mon_hoc_yeu_thich": "Sinh",
        "ky_nang_noi_bat": "Cẩn thận",
        "tinh_cach": "Kiên nhẫn",
        "moi_truong_lam_viec_mong_muon": "Bệnh viện",
        "muc_tieu_nghe_nghiep": "Cống hiến xã hội",
        "mo_ta_ban_than": "Em muốn giúp đỡ người bệnh và làm việc có ích cho cộng đồng.",
        "dinh_huong_tuong_lai": "Em muốn học điều dưỡng hoặc kỹ thuật xét nghiệm y học.",
    },
    {
        "so_thich_chinh": "Y tế",
        "mon_hoc_yeu_thich": "Hóa",
        "ky_nang_noi_bat": "Giải quyết vấn đề",
        "tinh_cach": "Trách nhiệm",
        "moi_truong_lam_viec_mong_muon": "Bệnh viện",
        "muc_tieu_nghe_nghiep": "Ổn định",
        "mo_ta_ban_than": "Em thích tìm hiểu thuốc, quy trình chăm sóc và an toàn sức khỏe.",
        "dinh_huong_tuong_lai": "Em muốn theo ngành dược học.",
    },
    {
        "so_thich_chinh": "Ngôn ngữ",
        "mon_hoc_yeu_thich": "Anh",
        "ky_nang_noi_bat": "Giao tiếp",
        "tinh_cach": "Hướng ngoại",
        "moi_truong_lam_viec_mong_muon": "Linh hoạt",
        "muc_tieu_nghe_nghiep": "Trải nghiệm quốc tế",
        "mo_ta_ban_than": "Em yêu thích ngoại ngữ và giao lưu với nhiều nền văn hóa.",
        "dinh_huong_tuong_lai": "Em muốn làm biên phiên dịch hoặc công việc đối ngoại.",
    },
    {
        "so_thich_chinh": "Ngôn ngữ",
        "mon_hoc_yeu_thich": "Văn",
        "ky_nang_noi_bat": "Thuyết trình",
        "tinh_cach": "Bản lĩnh",
        "moi_truong_lam_viec_mong_muon": "Trường học",
        "muc_tieu_nghe_nghiep": "Cống hiến xã hội",
        "mo_ta_ban_than": "Em thích giảng giải kiến thức và hỗ trợ người khác học ngoại ngữ.",
        "dinh_huong_tuong_lai": "Em muốn trở thành giáo viên tiếng Anh.",
    },
    {
        "so_thich_chinh": "Pháp lý",
        "mon_hoc_yeu_thich": "Văn",
        "ky_nang_noi_bat": "Giải quyết vấn đề",
        "tinh_cach": "Bản lĩnh",
        "moi_truong_lam_viec_mong_muon": "Văn phòng",
        "muc_tieu_nghe_nghiep": "Phát triển chuyên môn",
        "mo_ta_ban_than": "Em thích tranh luận logic, phân tích tình huống và bảo vệ quan điểm.",
        "dinh_huong_tuong_lai": "Em muốn theo ngành luật hoặc luật kinh tế.",
    },
    {
        "so_thich_chinh": "Giáo dục",
        "mon_hoc_yeu_thich": "Toán",
        "ky_nang_noi_bat": "Thuyết trình",
        "tinh_cach": "Kiên nhẫn",
        "moi_truong_lam_viec_mong_muon": "Trường học",
        "muc_tieu_nghe_nghiep": "Cống hiến xã hội",
        "mo_ta_ban_than": "Em thích hướng dẫn bạn bè học tập và giải bài chi tiết.",
        "dinh_huong_tuong_lai": "Em muốn trở thành giáo viên hoặc giảng viên.",
    },
    {
        "so_thich_chinh": "Công nghệ",
        "mon_hoc_yeu_thich": "Lý",
        "ky_nang_noi_bat": "Giải quyết vấn đề",
        "tinh_cach": "Tỉ mỉ",
        "moi_truong_lam_viec_mong_muon": "Kỹ thuật",
        "muc_tieu_nghe_nghiep": "Phát triển chuyên môn",
        "mo_ta_ban_than": "Em hứng thú với robot, mạch điện và điều khiển tự động.",
        "dinh_huong_tuong_lai": "Em muốn học kỹ thuật điện - điện tử hoặc tự động hóa.",
    },
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "major-recommendation-dev-secret")
MAX_CHAT_HISTORY = 20


def normalize_chat_history(history: list) -> list:
    """Làm sạch lịch sử chat và chỉ giữ role/content hợp lệ."""
    if not isinstance(history, list):
        return []

    cleaned = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()
        if role not in {"user", "assistant"} or not content:
            continue
        cleaned.append({"role": role, "content": content})

    return cleaned[-MAX_CHAT_HISTORY:]


def merge_chat_histories(*histories: list) -> list:
    """Gộp nhiều nguồn lịch sử chat theo thứ tự, loại bỏ bản ghi trùng."""
    merged = []
    seen = set()

    for history in histories:
        for item in normalize_chat_history(history):
            key = (item["role"], item["content"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)

    return merged[-MAX_CHAT_HISTORY:]


def get_chat_history() -> list:
    """Lấy 20 lượt chat gần nhất từ session."""
    history = session.get("chat_history", [])
    if not isinstance(history, list):
        return []
    return normalize_chat_history(history)


def save_chat_turn(user_message: str, bot_reply: str, base_history: list | None = None) -> None:
    """Lưu lượt chat vào session và chỉ giữ 20 lượt gần nhất."""
    history = normalize_chat_history(base_history if base_history is not None else get_chat_history())

    if not history or history[-1].get("role") != "user" or history[-1].get("content") != user_message:
        history.append({"role": "user", "content": user_message})

    history.append({"role": "assistant", "content": bot_reply})
    session["chat_history"] = history[-MAX_CHAT_HISTORY:]
    session.modified = True


def get_active_major() -> str:
    """Lấy major đang được chọn gần nhất trong session."""
    return str(session.get("active_major", "")).strip()


def set_active_major(major_key: str) -> None:
    """Lưu major đang active vào session."""
    session["active_major"] = str(major_key).strip()
    session.modified = True


def get_active_topic() -> str:
    """Lấy chủ đề đang được hỏi gần nhất trong session."""
    return str(session.get("active_topic", "")).strip()


def set_active_topic(topic: str) -> None:
    """Lưu chủ đề đang active vào session."""
    session["active_topic"] = str(topic).strip()
    session.modified = True


BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_DATA_PATH = BASE_DIR / "feedback_data.json"
FALLBACK_PENDING_DATA_PATH = BASE_DIR / "data" / "fallback_pending_samples.json"
_fallback_pending_lock = Lock()


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    text = text.replace("&", " va ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


FORM_ALLOWED_LABELS: Dict[str, list[str]] = {
    "so_thich_chinh": ["Công nghệ", "Kinh doanh", "Du lịch", "Nghệ thuật", "Y tế", "Ngôn ngữ", "Pháp lý", "Giáo dục"],
    "mon_hoc_yeu_thich": ["Toán", "Văn", "Anh", "Tin học", "Sinh", "Hóa", "Sử", "Địa", "Lý"],
    "ky_nang_noi_bat": [
        "Phân tích dữ liệu",
        "Giao tiếp",
        "Thuyết trình",
        "Sáng tạo",
        "Lãnh đạo",
        "Tổ chức & lập kế hoạch",
        "Tư duy logic",
        "Giải quyết vấn đề",
        "Cẩn thận",
        "Làm việc nhóm",
    ],
    "tinh_cach": ["Hướng nội", "Hướng ngoại", "Tỉ mỉ", "Năng động", "Kiên nhẫn", "Kỷ luật", "Trách nhiệm", "Bản lĩnh", "Quyết đoán"],
    "moi_truong_lam_viec_mong_muon": ["Kỹ thuật", "Văn phòng", "Linh hoạt", "Bệnh viện", "Trường học"],
    "muc_tieu_nghe_nghiep": ["Ổn định", "Phát triển chuyên môn", "Thu nhập cao", "Theo đam mê", "Trải nghiệm quốc tế", "Khởi nghiệp", "Cống hiến xã hội"],
}

FORM_ALLOWED_NORMALIZED = {
    field: {_normalize_text(label) for label in labels}
    for field, labels in FORM_ALLOWED_LABELS.items()
}

FORM_CANONICAL_BY_NORMALIZED = {
    field: {_normalize_text(label): label for label in labels}
    for field, labels in FORM_ALLOWED_LABELS.items()
}


def _find_unmatched_categorical_fields(payload: Dict[str, Any]) -> Dict[str, str]:
    unmatched: Dict[str, str] = {}
    for field in CATEGORICAL_COLS:
        raw_value = str(payload.get(field, "") or "").strip()
        norm_value = _normalize_text(raw_value)
        if not norm_value:
            continue
        if norm_value not in FORM_ALLOWED_NORMALIZED.get(field, set()):
            unmatched[field] = raw_value
    return unmatched


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    candidate = str(text or "").strip()
    if not candidate:
        return None
    if candidate.startswith("{") and candidate.endswith("}"):
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        parsed = json.loads(candidate[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _build_form_fallback_prompt(payload: Dict[str, Any], unmatched_fields: Dict[str, str]) -> str:
    allowed_lines = []
    for field, labels in FORM_ALLOWED_LABELS.items():
        allowed_lines.append(f"- {field}: {', '.join(labels)}")

    current_profile = []
    for field in list(CATEGORICAL_COLS) + ["mo_ta_ban_than", "dinh_huong_tuong_lai"]:
        current_profile.append(f"- {field}: {str(payload.get(field, '')).strip()}")

    unmatched_desc = "\n".join(f"- {k}: {v}" for k, v in unmatched_fields.items())
    allowed_block = "\n".join(allowed_lines)
    current_profile_block = "\n".join(current_profile)

    return (
        "Bạn là bộ chuẩn hóa dữ liệu form tư vấn ngành học.\n"
        "Nhiệm vụ: map các giá trị không chuẩn về đúng nhãn hợp lệ cho 6 trường categorical.\n"
        "Chỉ trả về JSON object hợp lệ, không thêm giải thích, không markdown.\n\n"
        "Danh sách nhãn hợp lệ:\n"
        f"{allowed_block}\n\n"
        "Dữ liệu đầu vào hiện tại:\n"
        f"{current_profile_block}\n\n"
        "Các trường chưa khớp nhãn:\n"
        f"{unmatched_desc}\n\n"
        "Hãy trả về đúng cấu trúc:\n"
        "{\n"
        '  "normalized_fields": {\n'
        '    "so_thich_chinh": "...",\n'
        '    "mon_hoc_yeu_thich": "...",\n'
        '    "ky_nang_noi_bat": "...",\n'
        '    "tinh_cach": "...",\n'
        '    "moi_truong_lam_viec_mong_muon": "...",\n'
        '    "muc_tieu_nghe_nghiep": "..."\n'
        "  },\n"
        '  "confidence": 0.0\n'
        "}\n"
    )


def _normalize_payload_via_fallback(payload: Dict[str, Any], unmatched_fields: Dict[str, str]) -> Optional[Dict[str, Any]]:
    prompt = _build_form_fallback_prompt(payload, unmatched_fields)
    fallback_chain = [
        ("deepseek", get_deepseek_fallback_api),
        ("openai", get_openai_fallback_api),
        ("claude", get_claude_fallback_api),
        ("last", get_last_fallback_api),
    ]

    for source_name, factory in fallback_chain:
        try:
            api = factory()
            result = api.analyze_free_text(prompt, context="form")
            if not isinstance(result, dict) or not result.get("success"):
                continue

            parsed = _extract_json_object(result.get("response", ""))
            if not parsed:
                continue

            normalized_fields = parsed.get("normalized_fields", {})
            if not isinstance(normalized_fields, dict):
                continue

            merged_payload = dict(payload)
            changed_fields: Dict[str, str] = {}
            for field in CATEGORICAL_COLS:
                proposed = str(normalized_fields.get(field, "") or "").strip()
                if not proposed:
                    continue
                norm_proposed = _normalize_text(proposed)
                canonical = FORM_CANONICAL_BY_NORMALIZED.get(field, {}).get(norm_proposed)
                if not canonical:
                    continue
                merged_payload[field] = canonical
                changed_fields[field] = canonical

            still_unmatched = _find_unmatched_categorical_fields(merged_payload)
            if still_unmatched:
                continue

            confidence = parsed.get("confidence", 0.0)
            try:
                confidence = float(confidence)
            except Exception:
                confidence = 0.0

            return {
                "payload": merged_payload,
                "changed_fields": changed_fields,
                "source": source_name,
                "confidence": round(confidence, 3),
            }
        except Exception as exc:
            logger.warning("Form fallback %s failed: %s", source_name, exc)

    return None


def _append_pending_fallback_sample(original_payload: Dict[str, Any], normalized_payload: Dict[str, Any], meta: Dict[str, Any]) -> None:
    from datetime import datetime

    FALLBACK_PENDING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "original_payload": original_payload,
        "normalized_payload": normalized_payload,
        "meta": meta,
    }

    with _fallback_pending_lock:
        existing: Dict[str, Any] = {"samples": []}
        if FALLBACK_PENDING_DATA_PATH.exists():
            try:
                existing = json.loads(FALLBACK_PENDING_DATA_PATH.read_text(encoding="utf-8"))
                if not isinstance(existing, dict):
                    existing = {"samples": []}
            except Exception:
                existing = {"samples": []}

        samples = existing.get("samples", [])
        if not isinstance(samples, list):
            samples = []
        samples.append(entry)
        existing["samples"] = samples[-2000:]
        FALLBACK_PENDING_DATA_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


@lru_cache(maxsize=1)
def load_feedback_data() -> dict:
    """Load cached dữ liệu phản hồi từ file JSON. Chỉ load 1 lần."""
    try:
        with FEEDBACK_DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning(f"Không load được feedback data: {exc}")
        return {}


class ModelManager:
    """Quản lý model state một cách sạch sẽ (thay thế global variables)."""

    def __init__(self):
        self._lock = Lock()
        self._predictor: Optional[Predictor] = None
        self._model_ready: bool = False
        self._model_error: str = ""
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Khởi tạo model lần đầu."""
        try:
            self._predictor = load_predictor()
            self._model_ready = True
            self._model_error = ""
            logger.info("✓ Model loaded successfully")
        except Exception as exc:
            self._model_ready = False
            self._model_error = str(exc)
            logger.error(f"✗ Failed to load model: {exc}")

    def ensure_ready(self) -> bool:
        """Đảm bảo model sẵn sàng, thử load lại nếu cần."""
        if self._model_ready and self._predictor is not None:
            return True

        try:
            self._predictor = load_predictor()
            self._model_ready = True
            self._model_error = ""
            logger.info("✓ Model reloaded successfully")
            return True
        except Exception as exc:
            self._model_error = str(exc)
            logger.error(f"✗ Failed to reload model: {exc}")
            return False

    @property
    def predictor(self) -> Optional[Predictor]:
        """Lấy predictor (có thể None nếu model chưa ready)."""
        return self._predictor

    @property
    def is_ready(self) -> bool:
        """Kiểm tra xem model có sẵn sàng không."""
        return self._model_ready

    @property
    def error_message(self) -> str:
        """Lấy thông báo lỗi nếu có."""
        return self._model_error


model_manager = ModelManager()


@app.route("/")
def home():
    """Hiển thị form nhập liệu."""
    return render_template(
        "index.html",
        model_ready=model_manager.is_ready,
        model_error=model_manager.error_message,
    )


@app.route("/chatbot")
def chatbot_page():
    """Hiển thị trang chatbot full-screen kiểu ChatGPT."""
    # FIX: Clear session history when entering chatbot page
    # This ensures fresh start whenever user reloads or navigates to chatbot
    session.pop("chat_history", None)
    session.pop("active_major", None)
    session.pop("active_topic", None)
    session.modified = True
    logger.info("🔄 Chatbot page loaded - session history cleared for fresh start")
    return render_template("chatbot.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "model_ready": model_manager.is_ready,
        "error": model_manager.error_message if not model_manager.is_ready else None,
    })


@app.route("/sample-profiles", methods=["GET"])
def sample_profiles():
    """Trả về 10 hồ sơ mẫu ngẫu nhiên theo schema form hiện tại."""
    sample_size = min(10, len(SAMPLE_PROFILES))
    samples = random.sample(SAMPLE_PROFILES, k=sample_size)
    return jsonify({
        "samples": samples,
        "count": len(samples),
    }), 200


def format_top3_results(results: list, feedback_data: dict) -> list:
    """Format kết quả top 3 theo 3 nhóm dễ hiểu cho người dùng."""
    majors_data = feedback_data.get("majors", {})
    formatted_top3 = []

    group_action_map = {
        "Công nghệ - Kỹ thuật": "Thử một dự án nhỏ hoặc bài test thực hành để kiểm tra độ phù hợp thực tế.",
        "Kinh doanh - Tài chính - Quản trị": "Thử case study, phân tích thị trường hoặc hoạt động quản lý nhóm nhỏ.",
        "Xã hội - Nhân văn - Giáo dục - Luật": "Thử viết, thuyết trình, tranh luận hoặc quan sát môi trường học tập phù hợp.",
        "Sức khỏe - Dịch vụ cộng đồng": "Tìm hiểu kỹ cường độ học, thực tập và mức độ phù hợp với việc chăm sóc người khác.",
        "Sáng tạo - Truyền thông - Du lịch - Kiến trúc": "Làm một portfolio nhỏ hoặc sản phẩm mẫu để đánh giá khả năng sáng tạo và giao tiếp.",
    }

    for idx, item in enumerate(results):
        major_key = item.get("nganh") or item.get("major") or ""
        major_name = MAJOR_DISPLAY.get(major_key, major_key)
        group_name = MAJOR_GROUPS.get(major_key, "Khác")
        raw_suggestions = majors_data.get(major_key, {}).get("suggestions", [])
        suggestion = SUGGESTION_VI.get(major_key, raw_suggestions[0] if raw_suggestions else "")

        final_score = float(item.get("score_final", item.get("absolute_score", item.get("score", 0))) or 0)
        display_score = float(item.get("score_display", final_score) or 0)
        relative_score = float(item.get("score_relative", 0) or 0)
        raw_score = float(item.get("raw_score", 0) or 0)
        next_raw = float(results[idx + 1].get("raw_score", 0) or 0) if idx + 1 < len(results) else 0.0
        raw_gap = raw_score - next_raw
        margin_score = max(0.0, min(100.0, raw_gap * 160.0))

        if idx == 0:
            tier_key = "best"
            tier_label = "Hướng phù hợp nhất"
            if final_score >= 70:
                tier_note = "Đây là lựa chọn nổi bật nhất hiện tại và có nhiều tín hiệu đồng thuận từ hồ sơ của bạn."
            elif final_score >= 50:
                tier_note = "Đây là lựa chọn nổi bật nhất hiện tại, nhưng vẫn nên đối chiếu thêm với sở thích thực tế."
            else:
                tier_note = "Đây là lựa chọn đứng đầu danh sách hiện tại, nhưng mức phù hợp còn thấp nên hãy xem như hướng tham khảo."
        elif idx == 1:
            tier_key = "consider"
            tier_label = "Hướng nên cân nhắc"
            if final_score >= 55:
                tier_note = "Ngành này khá sát với hồ sơ của bạn và đáng để so sánh trực tiếp với lựa chọn đứng đầu."
            else:
                tier_note = "Ngành này có tiềm năng, nhưng cần thêm dữ liệu về sở thích và trải nghiệm thực tế để xác nhận."
        else:
            tier_key = "explore"
            tier_label = "Hướng nên khám phá thêm"
            if final_score >= 45:
                tier_note = "Ngành này vẫn đáng khám phá nếu bạn có hứng thú hoặc mục tiêu nghề nghiệp rõ ràng."
            else:
                tier_note = "Ngành này phù hợp thấp hơn, nhưng vẫn có thể là phương án dự phòng để mở rộng lựa chọn."

        feedback = f"{tier_label} cho ngành {major_name}."
        confidence_text = f"{tier_label}. {tier_note}"
        next_step = group_action_map.get(group_name, "Thử tìm hiểu thêm bằng một bài test ngắn, dự án nhỏ hoặc buổi tư vấn trực tiếp.")

        formatted_top3.append({
            # Keep both key/display fields so frontend never has to guess.
            "nganh": major_key,
            "major": major_name,
            "major_key": major_key,
            "major_display": major_name,
            "group": group_name,
            "score": round(display_score, 2),
            "score_display": round(display_score, 2),
            "score_fit": round(final_score, 2),
            "score_final": round(final_score, 2),
            "score_relative": round(relative_score, 2),
            "raw_score": round(raw_score, 4),
            "margin_score": round(margin_score, 2),
            "tier": tier_key,
            "confidence_text": confidence_text,
            "feedback": feedback,
            "suggestion": suggestion,
            "next_step": next_step,
        })

    return formatted_top3


@app.route("/predict", methods=["POST"])
def predict():
    """API endpoint dự đoán ngành phù hợp."""
    if not model_manager.ensure_ready():
        return jsonify({"error": model_manager.error_message}), 500

    data = request.get_json(silent=True) or {}
    required_fields = list(CATEGORICAL_COLS) + ["mo_ta_ban_than", "dinh_huong_tuong_lai"]
    working_payload = dict(data)
    normalized_data = row_dict_from_payload(working_payload)
    for field in ["mo_ta_ban_than", "dinh_huong_tuong_lai"]:
        normalized_data[field] = str(working_payload.get(field, "") or "").strip()
    missing = [field for field in required_fields if not str(working_payload.get(field, "")).strip()]
    if missing:
        missing_labels = []
        for field in missing:
            if field == "mo_ta_ban_than":
                missing_labels.append("Mô tả bản thân")
            elif field == "dinh_huong_tuong_lai":
                missing_labels.append("Định hướng tương lai")
            else:
                missing_labels.append(field)
        return jsonify({"error": f"Vui lòng nhập đầy đủ các trường bắt buộc: {', '.join(missing_labels)}"}), 400

    fallback_used = False
    fallback_meta: Dict[str, Any] = {
        "used": False,
        "source": "",
        "confidence": 0.0,
        "changed_fields": {},
    }

    unmatched_fields = _find_unmatched_categorical_fields(working_payload)
    if unmatched_fields:
        fallback_result = _normalize_payload_via_fallback(working_payload, unmatched_fields)
        if fallback_result:
            fallback_used = True
            working_payload = dict(fallback_result.get("payload", working_payload))
            normalized_data = row_dict_from_payload(working_payload)
            for field in ["mo_ta_ban_than", "dinh_huong_tuong_lai"]:
                normalized_data[field] = str(working_payload.get(field, "") or "").strip()

            fallback_meta = {
                "used": True,
                "source": str(fallback_result.get("source", "")),
                "confidence": float(fallback_result.get("confidence", 0.0) or 0.0),
                "changed_fields": dict(fallback_result.get("changed_fields", {}) or {}),
                "unmatched_fields": unmatched_fields,
            }

            _append_pending_fallback_sample(
                original_payload=dict(data),
                normalized_payload=dict(working_payload),
                meta=fallback_meta,
            )

    try:
        result = model_manager.predictor.predict(normalized_data)
    except Exception as exc:
        logger.error(f"Prediction error: {exc}")
        return jsonify({"error": f"Lỗi khi dự đoán: {str(exc)}"}), 500

    feedback_data = load_feedback_data()
    ranked_items = result.get("top_3", [])
    formatted_top3 = format_top3_results(ranked_items, feedback_data)

    return jsonify({
        "top_3": formatted_top3,
        "giai_thich": result.get("giai_thich", []),
        "cong_thuc": result.get("cong_thuc", {}),
        "top_5_diem_tho": result.get("top_5_diem_tho", []),
        "major_groups": sorted(set(MAJOR_GROUPS.values())),
        "major_count": len(getattr(model_manager.predictor, "major_names", [])) if model_manager.predictor else 0,
        "fallback_used": fallback_used,
        "fallback_meta": fallback_meta,
        "train_warning": "Du lieu co 60+ nghe khoa hoc, model da toi uu de dua ra dieu nien va chinh xac.",
    })


def load_user_feedback() -> dict:
    """Load dữ liệu phản hồi người dùng từ file JSON."""
    try:
        with open(BASE_DIR / "user_feedback.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"feedbacks": []}
    except Exception as exc:
        logger.warning(f"Không load được user feedback: {exc}")
        return {"feedbacks": []}


def save_user_feedback(data: dict) -> None:
    """Lưu dữ liệu phản hồi người dùng vào file JSON."""
    try:
        with open(BASE_DIR / "user_feedback.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error(f"Lỗi khi lưu feedback: {exc}")


@app.route("/feedback", methods=["POST"])
def save_feedback():
    """Nhận và lưu feedback từ người dùng."""
    data = request.get_json(silent=True) or {}

    major = str(data.get("major", "")).strip()
    major_display = str(data.get("major_display", "")).strip()
    rating = data.get("rating")
    comment = str(data.get("comment", "")).strip()

    if not major or not major_display:
        return jsonify({"error": "Thiếu thông tin ngành"}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating phải từ 1 đến 5"}), 400

    try:
        from datetime import datetime

        feedback_data = load_user_feedback()
        new_feedback = {
            "id": f"f_{len(feedback_data.get('feedbacks', [])) + 1:04d}",
            "timestamp": datetime.now().isoformat(),
            "major": major,
            "major_display": major_display,
            "rating": rating,
            "comment": comment,
        }

        if "feedbacks" not in feedback_data:
            feedback_data["feedbacks"] = []

        feedback_data["feedbacks"].append(new_feedback)
        save_user_feedback(feedback_data)

        logger.info(f"Feedback saved for {major_display}: {rating} stars")
        return jsonify({"success": True, "message": "Cảm ơn đánh giá của bạn!"}), 200
    except Exception as exc:
        logger.error(f"Lỗi khi lưu feedback: {exc}")
        return jsonify({"error": f"Lỗi khi lưu feedback: {str(exc)}"}), 500


@app.route("/feedback-stats", methods=["GET"])
def get_feedback_stats():
    """Trả về thống kê feedback cho các ngành."""
    try:
        feedback_data = load_user_feedback()
        feedbacks = feedback_data.get("feedbacks", [])

        stats = {}
        for fb in feedbacks:
            major = fb.get("major", "")
            rating = fb.get("rating", 0)

            if major not in stats:
                stats[major] = {
                    "major": fb.get("major_display", major),
                    "ratings": [],
                    "count": 0,
                    "average": 0.0,
                }

            stats[major]["ratings"].append(rating)
            stats[major]["count"] += 1

        for major_key, stat in stats.items():
            if stat["ratings"]:
                stat["average"] = round(sum(stat["ratings"]) / len(stat["ratings"]), 1)

        return jsonify({"total_feedbacks": len(feedbacks), "majors": stats}), 200
    except Exception as exc:
        logger.error(f"Lỗi khi lấy thống kê feedback: {exc}")
        return jsonify({"error": "Lỗi khi lấy thống kê"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """API endpoint cho chatbot tư vấn ngành học."""
    if not model_manager.ensure_ready():
        return jsonify({"error": "Model chưa sẵn sàng"}), 500

    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    provided_history = data.get("history")
    user_profile = data.get("user_profile", {})  # Get saved user profile from frontend
    
    if not isinstance(user_profile, dict):
        user_profile = {}

    if not user_message:
        return jsonify({"error": "Vui lòng nhập tin nhắn"}), 400

    try:
        chatbot = MajorChatbot(model_manager.predictor)
        session_history = get_chat_history()
        client_history = normalize_chat_history(provided_history) if isinstance(provided_history, list) else []
        history = merge_chat_histories(session_history, client_history)
        
        # Log user profile for debugging
        if user_profile:
            logger.info(f"✅ Using user profile from frontend: {list(user_profile.keys())}")

        explicit_major = chatbot._find_major_in_text(user_message)
        is_followup_like = chatbot._is_followup_question(user_message)
        previous_active_major = get_active_major()
        context_major = chatbot._extract_context_major(
            history,
            current_message=user_message,
        )

        # Khong de major cu trong session lam lech cac cau hoi mo ho kieu
        # "hoc nganh nao" hoac "diem thi ..." neu user khong dang hoi tiep.
        if explicit_major:
            active_major = explicit_major
        elif is_followup_like:
            active_major = previous_active_major or context_major
        else:
            active_major = context_major
        if active_major:
            set_active_major(active_major)

        detected_topic = chatbot._detect_followup_topic(user_message)
        previous_active_topic = get_active_topic()
        active_topic = detected_topic or (previous_active_topic if is_followup_like else "")
        if active_topic:
            set_active_topic(active_topic)

        response = chatbot.chat(
            user_message,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            feedback_data=load_feedback_data(),
        )

        # Ensure response has required fields
        if not isinstance(response, dict):
            logger.error(f"❌ Invalid response type from chatbot: {type(response)}")
            return jsonify({"error": "Lỗi khi xử lý tin nhắn"}), 500

        # Validate response has critical fields
        if not response.get("reply"):
            logger.error(f"❌ Response missing 'reply' field: {response.keys()}")
            response["reply"] = "Xin lỗi, mình không thể trả lời câu hỏi này lúc này. Hãy thử lại sau."

        # NEW: Validate response using ResponseValidator
        # FIX: Pass major_list for fallback API constraint
        try:
            validator = ResponseValidator()
            fallback_api = get_openai_fallback_api()
            major_list = load_major_list()
            response = validator.validate_response(
                user_message=user_message,
                response=response,
                fallback_api=fallback_api,
                major_list=major_list,
            )
            logger.info(f"✅ Response validation complete: {response.get('validation_passed', 'N/A')}")
        except Exception as val_exc:
            logger.warning(f"⚠️ Response validation failed (non-critical): {val_exc}")
            # Continue even if validation fails - don't block the response

        resolved_major = str(response.get("resolved_major", "") or active_major or "").strip()
        resolved_topic = str(response.get("resolved_topic", "") or active_topic or "").strip()
        if response.get("needs_clarification"):
            session.pop("active_major", None)
            session.pop("active_topic", None)
            session.modified = True
        elif resolved_major:
            set_active_major(resolved_major)
        if not response.get("needs_clarification") and resolved_topic:
            set_active_topic(resolved_topic)

        save_chat_turn(user_message, response.get("reply", ""), base_history=history)
        logger.info(f"✅ Chat response returned successfully: {response.get('source', 'unknown')}")
        return jsonify(response), 200
    except Exception as exc:
        logger.error(f"❌ Chat error: {exc}", exc_info=True)
        return jsonify({"error": f"Lỗi khi xử lý tin nhắn: {str(exc)}"}), 500


@app.route("/chat/fallback", methods=["POST"])
def chat_fallback():
    """API endpoint gọi trực tiếp AI fallback cho chatbot."""
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    provided_history = data.get("history")
    active_major = str(data.get("active_major", "")).strip()
    active_topic = str(data.get("active_topic", "")).strip()
    context = str(data.get("context", "chatbot")).strip() or "chatbot"

    if not user_message:
        return jsonify({"error": "Vui lòng nhập tin nhắn"}), 400

    history = normalize_chat_history(provided_history) if isinstance(provided_history, list) else []

    try:
        # FIX: Load major_list for fallback API constraint
        major_list = load_major_list()
        
        deepseek_api = get_deepseek_fallback_api()
        deepseek_result = deepseek_api.analyze_free_text(
            user_message,
            context=context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            major_list=major_list,
        )
        if isinstance(deepseek_result, dict) and deepseek_result.get("success"):
            return jsonify(deepseek_result), 200
        
        openai_api = get_openai_fallback_api()
        openai_result = openai_api.analyze_free_text(
            user_message,
            context=context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            major_list=major_list,
        )
        if isinstance(openai_result, dict) and openai_result.get("success"):
            return jsonify(openai_result), 200

        claude_api = get_claude_fallback_api()
        claude_result = claude_api.analyze_free_text(
            user_message,
            context=context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            major_list=major_list,
        )
        if isinstance(claude_result, dict) and claude_result.get("success"):
            return jsonify(claude_result), 200

        last_fallback_api = get_last_fallback_api()
        last_result = last_fallback_api.analyze_free_text(
            user_message,
            context=context,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            major_list=major_list,
        )
        if isinstance(last_result, dict) and last_result.get("success"):
            return jsonify(last_result), 200

        return jsonify({
            "success": False,
            "response": "",
            "source": "fallback_chain",
            "error": (deepseek_result or {}).get("error") or (openai_result or {}).get("error") or (claude_result or {}).get("error") or (last_result or {}).get("error") or "Fallback API unavailable",
        }), 502
    except Exception as exc:
        logger.error(f"Chat fallback error: {exc}")
        return jsonify({"error": f"Lỗi khi gọi fallback API: {str(exc)}"}), 500


@app.errorhandler(404)
def not_found(error):
    """Xử lý 404 errors."""
    return jsonify({"error": "Endpoint không tồn tại"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Xử lý 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Lỗi server nội bộ"}), 500


if __name__ == "__main__":
    import os
    # Get port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Run on 0.0.0.0 to allow external connections (required for Replit)
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
