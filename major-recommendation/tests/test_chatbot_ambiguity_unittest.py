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
                "Cong nghe thong tin",
                "Marketing",
                "Quan tri kinh doanh",
                "Dieu khien va quan ly tau bien",
                "Khai thac may tau thuy va quan ly ky thuat",
            ],
            major_lookup={
                "Cong nghe thong tin": {"nganh": "Cong nghe thong tin", "mo_ta": "Lap trinh va he thong"},
                "Marketing": {"nganh": "Marketing", "mo_ta": "Truyen thong va thi truong"},
                "Quan tri kinh doanh": {"nganh": "Quan tri kinh doanh", "mo_ta": "Quan ly va chien luoc"},
                "Dieu khien va quan ly tau bien": {"nganh": "Dieu khien va quan ly tau bien", "mo_ta": "Hang hai va van hanh tau bien"},
                "Khai thac may tau thuy va quan ly ky thuat": {"nganh": "Khai thac may tau thuy va quan ly ky thuat", "mo_ta": "May tau thuy va ky thuat hang hai"},
            },
        )


def make_chatbot() -> MajorChatbot:
    chatbot = MajorChatbot(DummyPredictor())
    chatbot._get_tfidf_response = lambda *_args, **_kwargs: (None, 0.0)
    chatbot._get_fallback_response = lambda *_args, **_kwargs: "fallback reply"
    return chatbot


class ChatbotAmbiguityTests(unittest.TestCase):
    def test_asks_to_clarify_when_two_majors_appear_in_same_message(self):
        chatbot = make_chatbot()

        result = chatbot.chat("Em đang phân vân giữa CNTT và Marketing", history=[])

        self.assertEqual(result["source"], "context_clarify")
        self.assertTrue(result["needs_clarification"])
        self.assertIn("Bạn đang hỏi về", result["reply"])
        self.assertEqual(result["clarify_options"], ["Cong nghe thong tin", "Marketing"])

    def test_followup_with_new_explicit_major_switches_focus(self):
        chatbot = make_chatbot()
        history = [
            {"role": "user", "content": "Em muốn hỏi về CNTT"},
            {"role": "assistant", "content": "CNTT là ngành..."},
        ]

        result = chatbot.chat("Còn Marketing thì sao?", history=history, active_major="Cong nghe thong tin")

        self.assertEqual(result["source"], "explicit_major")
        self.assertFalse(result["needs_clarification"])
        self.assertEqual(result["resolved_major"], "Marketing")

    def test_followup_without_two_majors_still_answers_normally(self):
        chatbot = make_chatbot()
        history = [
            {"role": "user", "content": "Em muốn hỏi về Marketing"},
            {"role": "assistant", "content": "Marketing là ngành..."},
        ]

        result = chatbot.chat("Ngành này lương sao?", history=history)

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_major"], "Marketing")
        self.assertEqual(result["resolved_topic"], "salary")
        self.assertFalse(result["needs_clarification"])

    def test_major_selection_reply_should_not_trigger_ambiguity(self):
        chatbot = make_chatbot()
        history = [
            {
                "role": "assistant",
                "content": "Bạn muốn mình ước lượng lương theo từng vị trí của ngành Công nghệ thông tin hay ngành Điều khiển và quản lý tàu biển?",
            },
        ]

        result = chatbot.chat(
            "Khai thác máy tàu thủy và quản lý kỹ thuật",
            history=history,
            active_topic="salary",
        )

        self.assertNotEqual(result["source"], "context_clarify")
        self.assertFalse(result.get("needs_clarification", False))
        self.assertEqual(result["resolved_major"], "Khai thac may tau thuy va quan ly ky thuat")


if __name__ == "__main__":
    unittest.main()
