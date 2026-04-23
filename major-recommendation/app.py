import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Optional

from flask import Flask, jsonify, render_template, request, session

from utils.chatbot import MajorChatbot
from utils.constants import CATEGORICAL_COLS, MAJOR_DISPLAY, SUGGESTION_VI
from utils.fallback_api import get_fallback_api
from utils.predictor import Predictor, load_predictor

MAJOR_GROUPS = {
    "Cong nghe thong tin": "Công nghệ - Kỹ thuật",
    "Ky thuat phan mem": "Công nghệ - Kỹ thuật",
    "Khoa hoc du lieu": "Công nghệ - Kỹ thuật",
    "Tri tue nhan tao": "Công nghệ - Kỹ thuật",
    "An ninh mang": "Công nghệ - Kỹ thuật",
    "He thong thong tin": "Công nghệ - Kỹ thuật",
    "Ky thuat may tinh": "Công nghệ - Kỹ thuật",
    "Ky thuat dien dien tu": "Công nghệ - Kỹ thuật",
    "Tu dong hoa": "Công nghệ - Kỹ thuật",
    "Ky thuat co khi": "Công nghệ - Kỹ thuật",
    "Ky thuat o to": "Công nghệ - Kỹ thuật",
    "Ky thuat xay dung": "Công nghệ - Kỹ thuật",
    "Quan tri kinh doanh": "Kinh doanh - Tài chính - Quản trị",
    "Marketing": "Kinh doanh - Tài chính - Quản trị",
    "Thuong mai dien tu": "Kinh doanh - Tài chính - Quản trị",
    "Tai chinh ngan hang": "Kinh doanh - Tài chính - Quản trị",
    "Ke toan": "Kinh doanh - Tài chính - Quản trị",
    "Kiem toan": "Kinh doanh - Tài chính - Quản trị",
    "Logistics va quan ly chuoi cung ung": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri nhan luc": "Kinh doanh - Tài chính - Quản trị",
    "Kinh doanh quoc te": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri khach san": "Kinh doanh - Tài chính - Quản trị",
    "Quan tri nha hang va dich vu an uong": "Kinh doanh - Tài chính - Quản trị",
    "Khoi nghiep va doi moi sang tao": "Kinh doanh - Tài chính - Quản trị",
    "Ngon ngu Anh": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Trung": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Nhat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Ngon ngu Han": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Bao chi": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Truyen thong da phuong tien": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Quan he cong chung": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Luat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Luat kinh te": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Tam ly hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Cong tac xa hoi": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Su pham Toan hoc": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Y da khoa": "Sức khỏe - Dịch vụ cộng đồng",
    "Duoc hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Dieu duong": "Sức khỏe - Dịch vụ cộng đồng",
    "Ky thuat xet nghiem y hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Ky thuat hinh anh y hoc": "Sức khỏe - Dịch vụ cộng đồng",
    "Y hoc co truyen": "Sức khỏe - Dịch vụ cộng đồng",
    "Rang ham mat": "Sức khỏe - Dịch vụ cộng đồng",
    "Dinh duong": "Sức khỏe - Dịch vụ cộng đồng",
    "Y te cong cong": "Sức khỏe - Dịch vụ cộng đồng",
    "Ho sinh": "Sức khỏe - Dịch vụ cộng đồng",
    "Vat ly tri lieu va phuc hoi chuc nang": "Sức khỏe - Dịch vụ cộng đồng",
    "Quan ly benh vien": "Sức khỏe - Dịch vụ cộng đồng",
    "Thiet ke do hoa": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke thoi trang": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke noi that": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Kien truc": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "My thuat": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Nhiếp anh": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Quay phim - Dung phim": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Du lich": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Quan tri dich vu du lich va lu hanh": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Huong dan du lich": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Thiet ke game": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
    "Nghe thuat so": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
}

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
    return render_template("chatbot.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "model_ready": model_manager.is_ready,
        "error": model_manager.error_message if not model_manager.is_ready else None,
    })


def format_top3_results(results: list, feedback_data: dict) -> list:
    """Format kết quả top 3 từ model."""
    majors_data = feedback_data.get("majors", {})
    formatted_top3 = []

    for idx, item in enumerate(results):
        major_key = item.get("nganh") or item.get("major") or ""
        major_name = MAJOR_DISPLAY.get(major_key, major_key)
        raw_suggestions = majors_data.get(major_key, {}).get("suggestions", [])
        suggestion = SUGGESTION_VI.get(major_key, raw_suggestions[0] if raw_suggestions else "")

        feedback = str(item.get("feedback", "")).strip()
        if feedback:
            feedback = feedback[0].upper() + feedback[1:]

        relative_score = float(item.get("score", 0) or 0)
        fit_score = float(item.get("absolute_score", relative_score) or 0)
        raw_score = float(item.get("raw_score", 0) or 0)
        display_score = fit_score
        next_raw = float(results[idx + 1].get("raw_score", 0) or 0) if idx + 1 < len(results) else 0.0
        raw_gap = raw_score - next_raw
        margin_score = max(0.0, min(100.0, raw_gap * 160.0))
        confidence_score = 0.65 * fit_score + 0.35 * margin_score

        if confidence_score >= 72:
            confidence = "Cao"
            confidence_note = "Điểm phù hợp cao và đang tách biệt khá rõ với các lựa chọn phía sau."
        elif confidence_score >= 48:
            confidence = "Khá phù hợp"
            confidence_note = "Mức phù hợp tốt, nên xem thêm các ngành tương đồng để đối chiếu."
        else:
            confidence = "Tham khảo"
            confidence_note = "Mức phù hợp chưa đủ nổi bật, nên đối chiếu thêm trải nghiệm và sở thích thực tế."

        confidence_text = f"{confidence}. {confidence_note}" if confidence_note else confidence
        formatted_top3.append({
            "nganh": major_key,
            "major": major_name,
            "group": MAJOR_GROUPS.get(major_key, "Khác"),
            "score": round(display_score, 2),
            "score_fit": round(fit_score, 2),
            "score_relative": round(relative_score, 2),
            "score_type": "fit_display",
            "confidence": confidence,
            "confidence_text": confidence_text,
            "confidence_score": round(confidence_score, 1),
            "confidence_gap_raw": round(raw_gap, 4),
            "confidence_note": confidence_note,
            "feedback": feedback,
            "suggestion": suggestion,
        })

    return formatted_top3


@app.route("/predict", methods=["POST"])
def predict():
    """API endpoint dự đoán ngành phù hợp."""
    if not model_manager.ensure_ready():
        return jsonify({"error": model_manager.error_message}), 500

    data = request.get_json(silent=True) or {}
    required_fields = list(CATEGORICAL_COLS)
    missing = [field for field in required_fields if not str(data.get(field, "")).strip()]
    if missing:
        return jsonify({"error": f"Vui long nhap day du cac truong bat buoc: {', '.join(missing)}"}), 400

    try:
        result = model_manager.predictor.predict(data)
    except Exception as exc:
        logger.error(f"Prediction error: {exc}")
        return jsonify({"error": f"Lỗi khi dự đoán: {str(exc)}"}), 500

    feedback_data = load_feedback_data()
    ranked_items = result.get("top_3", [])
    formatted_top3 = format_top3_results(ranked_items, feedback_data)

    return jsonify({
        "top_3": formatted_top3,
        "major_groups": sorted(set(MAJOR_GROUPS.values())),
        "major_count": len(getattr(model_manager.predictor, "major_names", [])) if model_manager.predictor else 0,
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

    if not user_message:
        return jsonify({"error": "Vui lòng nhập tin nhắn"}), 400

    try:
        chatbot = MajorChatbot(model_manager.predictor)
        session_history = get_chat_history()
        client_history = normalize_chat_history(provided_history) if isinstance(provided_history, list) else []
        history = merge_chat_histories(session_history, client_history)

        explicit_major = chatbot._find_major_in_text(user_message)
        previous_active_major = get_active_major()
        active_major = explicit_major or previous_active_major or chatbot._extract_context_major(
            history,
            current_message=user_message,
        )
        if active_major:
            set_active_major(active_major)

        detected_topic = chatbot._detect_followup_topic(user_message)
        active_topic = detected_topic or get_active_topic()
        if active_topic:
            set_active_topic(active_topic)

        response = chatbot.chat(
            user_message,
            history=history,
            active_major=active_major,
            active_topic=active_topic,
            feedback_data=load_feedback_data(),
        )

        resolved_major = str(response.get("resolved_major", "") or active_major or "").strip()
        resolved_topic = str(response.get("resolved_topic", "") or active_topic or "").strip()
        if resolved_major:
            set_active_major(resolved_major)
        if resolved_topic:
            set_active_topic(resolved_topic)

        save_chat_turn(user_message, response.get("reply", ""), base_history=history)
        return jsonify(response), 200
    except Exception as exc:
        logger.error(f"Chat error: {exc}")
        return jsonify({"error": f"Lỗi khi xử lý tin nhắn: {str(exc)}"}), 500


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
    app.run(debug=True)
