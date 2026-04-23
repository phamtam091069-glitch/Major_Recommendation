from __future__ import annotations

import unittest
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
            major_names=[
                "Dieu khien va quan ly tau bien",
                "Khai thac may tau thuy va quan ly ky thuat",
                "Cong nghe thong tin",
            ],
            major_lookup={
                "Dieu khien va quan ly tau bien": {"nganh": "Dieu khien va quan ly tau bien", "mo_ta": "Hang hai va van hanh tau bien"},
                "Khai thac may tau thuy va quan ly ky thuat": {"nganh": "Khai thac may tau thuy va quan ly ky thuat", "mo_ta": "May tau thuy va ky thuat hang hai"},
                "Cong nghe thong tin": {"nganh": "Cong nghe thong tin", "mo_ta": "Lap trinh"},
            },
        )


def make_chatbot() -> MajorChatbot:
    chatbot = MajorChatbot(DummyPredictor())
    chatbot._get_tfidf_response = lambda *_args, **_kwargs: (None, 0.0)
    chatbot._get_fallback_response = lambda *_args, **_kwargs: "fallback reply"
    return chatbot


class MarineAliasTests(unittest.TestCase):
    def test_alias_detects_dieu_khien_va_quan_ly_tau_bien(self):
        chatbot = make_chatbot()

        self.assertEqual(
            chatbot._find_major_in_text("Em muốn tìm hiểu ngành hàng hải"),
            "Dieu khien va quan ly tau bien",
        )
        self.assertEqual(
            chatbot._find_major_in_text("Ngành marine"),
            "Dieu khien va quan ly tau bien",
        )

    def test_alias_detects_khai_thac_may_tau_thuy(self):
        chatbot = make_chatbot()

        self.assertEqual(
            chatbot._find_major_in_text("Em quan tâm ngành máy tàu thủy"),
            "Khai thac may tau thuy va quan ly ky thuat",
        )
        self.assertEqual(
            chatbot._find_major_in_text("marine engineering"),
            "Khai thac may tau thuy va quan ly ky thuat",
        )

    def test_followup_about_marine_major_uses_context(self):
        chatbot = make_chatbot()
        history = [
            {"role": "user", "content": "Em muốn hỏi về ngành hàng hải"},
            {"role": "assistant", "content": "Ngành này..."},
        ]

        result = chatbot.chat("Ngành này khó không?", history=history)

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_major"], "Dieu khien va quan ly tau bien")
        self.assertEqual(result["resolved_topic"], "difficulty")


if __name__ == "__main__":
    unittest.main()
