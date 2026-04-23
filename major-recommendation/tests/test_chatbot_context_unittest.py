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


class ChatbotContextTests(unittest.TestCase):
    def test_followup_uses_major_from_history(self):
        chatbot = make_chatbot()
        history = [
            {"role": "user", "content": "Em muốn tìm hiểu ngành Marketing"},
            {"role": "assistant", "content": "Marketing là ngành..."},
        ]

        result = chatbot.chat("Ngành này lương sao?", history=history)

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_major"], "Marketing")
        self.assertEqual(result["resolved_topic"], "salary")
        self.assertIn("Marketing", result["reply"])

    def test_followup_uses_active_major(self):
        chatbot = make_chatbot()

        result = chatbot.chat("Còn học phí?", history=[], active_major="Cong nghe thong tin")

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_major"], "Cong nghe thong tin")
        self.assertEqual(result["resolved_topic"], "tuition")
        self.assertIn("Công nghệ thông tin", result["reply"])

    def test_current_message_major_wins_over_history(self):
        chatbot = make_chatbot()
        history = [{"role": "user", "content": "Trước đó em hỏi ngành Marketing"}]

        result = chatbot.chat("Giờ em hỏi về Công nghệ thông tin thì sao?", history=history)

        self.assertEqual(result["resolved_major"], "Cong nghe thong tin")

    def test_non_followup_explicit_major_returns_overview(self):
        chatbot = make_chatbot()

        result = chatbot.chat("Em muốn hỏi về ngành Quản trị kinh doanh", history=[])

        self.assertEqual(result["resolved_major"], "Quan tri kinh doanh")
        self.assertEqual(result["resolved_topic"], "overview")
        self.assertEqual(result["source"], "explicit_major")

    def test_major_only_reply_after_salary_clarification_uses_active_topic(self):
        chatbot = make_chatbot()
        history = [
            {"role": "user", "content": "Bạn muốn mình ước lượng lương theo từng vị trí của ngành Công nghệ thông tin hay ngành Điều khiển và quản lý tàu biển?"},
            {"role": "assistant", "content": "Bạn muốn mình ước lượng lương theo từng vị trí của ngành Công nghệ thông tin hay ngành Điều khiển và quản lý tàu biển?"},
        ]

        result = chatbot.chat(
            "Công nghệ thông tin",
            history=history,
            active_major="Cong nghe thong tin",
            active_topic="salary",
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_major"], "Cong nghe thong tin")
        self.assertEqual(result["resolved_topic"], "salary")
        self.assertIn("Junior", result["reply"])
        self.assertIn("Số liệu trên chỉ mang tính chất tham khảo tùy thuộc vào thị trường việc làm.", result["reply"])

    def test_salary_prefers_major_benchmark_when_available(self):
        chatbot = make_chatbot()
        feedback_data = {
            "majors": {
                "Marketing": {
                    "salary_range": "12-25 triệu/tháng",
                }
            }
        }

        result = chatbot.chat(
            "Lương ngành này thế nào?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Marketing"}],
            active_major="Marketing",
            active_topic="salary",
            feedback_data=feedback_data,
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertIn("Mức lương tham khảo của ngành Marketing", result["reply"])
        self.assertIn("Nguồn tham khảo", result["reply"])
        self.assertIn("Số liệu trên chỉ mang tính chất tham khảo tùy thuộc vào thị trường việc làm.", result["reply"])

    def test_salary_uses_internal_numeric_data_when_benchmark_missing(self):
        chatbot = make_chatbot()
        feedback_data = {
            "majors": {
                "Quan tri kinh doanh": {
                    "salary_range": "11-23 triệu/tháng",
                }
            }
        }

        result = chatbot.chat(
            "Lương ngành này thế nào?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Quản trị kinh doanh"}],
            active_major="Quan tri kinh doanh",
            active_topic="salary",
            feedback_data=feedback_data,
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertIn("salary_range", result["reply"])
        self.assertIn("Số liệu trên chỉ mang tính chất tham khảo tùy thuộc vào thị trường việc làm.", result["reply"])

    def test_salary_estimate_fallback_includes_general_sources(self):
        chatbot = make_chatbot()

        result = chatbot.chat(
            "Lương ngành này thế nào?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Quản trị kinh doanh"}],
            active_major="Quan tri kinh doanh",
            active_topic="salary",
            feedback_data={},
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertIn("Nguồn tham khảo chung", result["reply"])
        self.assertIn("Chưa có benchmark riêng cho ngành này", result["reply"])
        self.assertIn("Số liệu trên chỉ mang tính chất tham khảo tùy thuộc vào thị trường việc làm.", result["reply"])

    def test_followup_hoc_gi_returns_study_content(self):
        chatbot = make_chatbot()

        result = chatbot.chat(
            "Ngành này học gì?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Điều khiển và quản lý tàu biển"}],
            active_major="Dieu khien va quan ly tau bien",
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_topic"], "study_content")
        self.assertIn("khối kiến thức cốt lõi", result["reply"])

    def test_followup_yeu_to_nao_returns_fit_factors(self):
        chatbot = make_chatbot()

        result = chatbot.chat(
            "Tôi muốn học ngành điều khiển tàu biển thì nên có những yếu tố nào?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Điều khiển và quản lý tàu biển"}],
            active_major="Dieu khien va quan ly tau bien",
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_topic"], "fit_factors")
        self.assertIn("Sức khỏe tốt", result["reply"])

    def test_followup_can_tien_de_hoc_maps_to_tuition_with_natural_reply(self):
        chatbot = make_chatbot()

        result = chatbot.chat(
            "Ngành này cần tiền để học không?",
            history=[{"role": "user", "content": "Em muốn tìm hiểu ngành Marketing"}],
            active_major="Marketing",
        )

        self.assertEqual(result["source"], "context_followup")
        self.assertEqual(result["resolved_topic"], "tuition")
        self.assertIn("Có nhé", result["reply"])

    def test_model_response_should_use_accented_major_display_from_constants(self):
        class ModelTfidf:
            def transform(self, _texts):
                return [[1.0]]

        predictor = SimpleNamespace(
            tfidf=ModelTfidf(),
            major_vectors=[[1.0]],
            major_names=["Quan tri nhan luc"],
            major_lookup={
                "Quan tri nhan luc": {
                    "nganh": "Quan tri nhan luc",
                    "major_display": "Quan tri nhan luc",
                    "mo_ta": "Đào tạo về tuyển dụng và phát triển đội ngũ.",
                }
            },
        )
        chatbot = MajorChatbot(predictor)

        result = chatbot.chat("Định hướng của tôi muốn làm doanh nhân", history=[])

        self.assertEqual(result["source"], "model")
        self.assertIn("Quản trị nhân lực", result["reply"])

    def test_off_topic_like_someone_should_be_scope_guarded(self):
        chatbot = make_chatbot()

        result = chatbot.chat("Tôi thích Linh", history=[])

        self.assertEqual(result["source"], "scope_guard")
        self.assertIn("tư vấn ngành học", result["reply"])

    def test_off_topic_want_love_relation_should_be_scope_guarded(self):
        chatbot = make_chatbot()

        result = chatbot.chat("Tôi muốn Linh làm người yêu", history=[])

        self.assertEqual(result["source"], "scope_guard")
        self.assertIn("không phù hợp để tư vấn chuyện tình cảm", result["reply"])


if __name__ == "__main__":
    unittest.main()
