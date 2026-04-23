from __future__ import annotations

from types import SimpleNamespace

from utils.chatbot import MajorChatbot


class DummyTfidf:
    def transform(self, _texts):
        return None


class DummyPredictor(SimpleNamespace):
    def __init__(self):
        super().__init__(
            tfidf=DummyTfidf(),
            major_vectors=None,
            major_names=["Cong nghe thong tin", "Marketing", "Quan tri kinh doanh"],
            major_lookup={
                "Cong nghe thong tin": {"nganh": "Cong nghe thong tin", "mo_ta": "Lap trinh va he thong"},
                "Marketing": {"nganh": "Marketing", "mo_ta": "Truyen thong va thi truong"},
                "Quan tri kinh doanh": {"nganh": "Quan tri kinh doanh", "mo_ta": "Quan ly va chien luoc"},
            },
        )


def make_chatbot() -> MajorChatbot:
    chatbot = MajorChatbot(DummyPredictor())
    chatbot._get_tfidf_response = lambda *_args, **_kwargs: (None, 0.0)
    chatbot._get_fallback_response = lambda *_args, **_kwargs: "fallback reply"
    return chatbot


def test_followup_uses_major_from_history_when_current_message_is_ambiguous():
    chatbot = make_chatbot()
    history = [
        {"role": "user", "content": "Em muốn tìm hiểu ngành Marketing"},
        {"role": "assistant", "content": "Marketing là ngành..."},
    ]

    result = chatbot.chat("Ngành này lương sao?", history=history)

    assert result["source"] == "context_followup"
    assert result["resolved_major"] == "Marketing"
    assert result["resolved_topic"] == "salary"
    assert "Marketing" in result["reply"]


def test_followup_uses_active_major_when_present():
    chatbot = make_chatbot()

    result = chatbot.chat("Còn học phí?", history=[], active_major="Cong nghe thong tin")

    assert result["source"] == "context_followup"
    assert result["resolved_major"] == "Cong nghe thong tin"
    assert result["resolved_topic"] == "tuition"
    assert "Công nghệ thông tin" in result["reply"]


def test_non_followup_question_resolves_major_from_current_message():
    chatbot = make_chatbot()

    result = chatbot.chat("Em muốn hỏi về ngành Quản trị kinh doanh", history=[])

    assert result["resolved_major"] == "Quan tri kinh doanh"
    assert result["resolved_topic"] == "overview"
    assert result["source"] == "fallback"


def test_context_major_prefers_current_message_over_history():
    chatbot = make_chatbot()
    history = [{"role": "user", "content": "Trước đó em hỏi ngành Marketing"}]

    result = chatbot.chat("Giờ em hỏi về Công nghệ thông tin thì sao?", history=history)

    assert result["resolved_major"] == "Cong nghe thong tin"


def test_health_followup_uses_existing_major_context():
    chatbot = make_chatbot()

    result = chatbot.chat(
        "Sức khỏe không tốt",
        history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Điều khiển và quản lý tàu biển"}],
        active_major="Dieu khien va quan ly tau bien",
        active_topic="fit_factors",
    )

    assert result["source"] == "context_followup"
    assert result["resolved_major"] == "Dieu khien va quan ly tau bien"
    assert result["resolved_topic"] == "fit_factors"


def test_hot_temper_followup_uses_existing_major_context():
    chatbot = make_chatbot()

    result = chatbot.chat(
        "Tính nóng phù hợp học ngành lái tàu không",
        history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Điều khiển và quản lý tàu biển"}],
        active_major="Dieu khien va quan ly tau bien",
        active_topic="fit_factors",
    )

    assert result["source"] == "context_followup"
    assert result["resolved_major"] == "Dieu khien va quan ly tau bien"
    assert result["resolved_topic"] == "fit_factors"


def test_hiv_followup_uses_existing_major_context():
    chatbot = make_chatbot()

    result = chatbot.chat(
        "Còn tôi bị HIV thì có học được ngành này không",
        history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Điều khiển và quản lý tàu biển"}],
        active_major="Dieu khien va quan ly tau bien",
        active_topic="fit_factors",
    )

    assert result["source"] == "context_followup"
    assert result["resolved_major"] == "Dieu khien va quan ly tau bien"
    assert result["resolved_topic"] == "fit_factors"
