from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert 'status' in response.get_json()


def test_predict_endpoint_accepts_current_form_vocab(monkeypatch):
    client = app.test_client()

    class DummyPredictor:
        major_names = ['Cong nghe thong tin', 'Khoa hoc du lieu', 'Marketing']

        def predict(self, payload):
            assert payload['so_thich_chinh'] == 'Du lich'
            assert payload['mon_hoc_yeu_thich'] == 'Anh'
            assert payload['ky_nang_noi_bat'] == 'To chuc va lap ke hoach'
            assert payload['tinh_cach'] == 'Huong ngoai'
            assert payload['moi_truong_lam_viec_mong_muon'] == 'Linh hoat'
            assert payload['muc_tieu_nghe_nghiep'] == 'Theo dam me'
            return {
                'top_3': [
                    {
                        'nganh': 'Huong dan du lich',
                        'score': 82.5,
                        'absolute_score': 82.5,
                        'raw_score': 82.5,
                        'feedback': 'Ban phu hop voi nganh nay.',
                    },
                    {
                        'nganh': 'Du lich',
                        'score': 75.0,
                        'absolute_score': 75.0,
                        'raw_score': 75.0,
                        'feedback': 'Ket qua tham khao.',
                    },
                    {
                        'nganh': 'Marketing',
                        'score': 61.0,
                        'absolute_score': 61.0,
                        'raw_score': 61.0,
                        'feedback': 'Ket qua tham khao.',
                    },
                ]
            }

    monkeypatch.setattr('app.model_manager.ensure_ready', lambda: True)
    monkeypatch.setattr('app.model_manager._predictor', DummyPredictor())

    response = client.post(
        '/predict',
        json={
            'so_thich_chinh': 'Du lich',
            'mon_hoc_yeu_thich': 'Anh',
            'ky_nang_noi_bat': 'To chuc va lap ke hoach',
            'tinh_cach': 'Huong ngoai',
            'moi_truong_lam_viec_mong_muon': 'Linh hoat',
            'muc_tieu_nghe_nghiep': 'Theo dam me',
            'mo_ta_ban_than': 'Em thich giao tiep va di chuyen.',
            'dinh_huong_tuong_lai': 'Em muon lam huong dan vien du lich.',
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['top_3'][0]['nganh'] == 'Huong dan du lich'
    assert payload['top_3'][0]['major'] == 'Hướng dẫn du lịch'


def test_chat_fallback_endpoint_returns_openai_result(monkeypatch):
    client = app.test_client()

    class DummyOpenAI:
        def analyze_free_text(self, user_text, context="chatbot", history=None, active_major="", active_topic=""):
            assert user_text == "Em hợp ngành nào?"
            assert context == "chatbot"
            assert active_major == "Marketing"
            assert active_topic == "overview"
            assert history == [{"role": "user", "content": "Em thích truyền thông"}]
            return {
                "success": True,
                "response": "Bạn có thể cân nhắc Marketing.",
                "source": "openai_fallback",
                "model": "test-openai",
            }

    monkeypatch.setattr("app.get_openai_fallback_api", lambda: DummyOpenAI())

    response = client.post(
        "/chat/fallback",
        json={
            "message": "Em hợp ngành nào?",
            "history": [{"role": "user", "content": "Em thích truyền thông"}],
            "active_major": "Marketing",
            "active_topic": "overview",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["source"] == "openai_fallback"


def test_chat_fallback_endpoint_uses_claude_when_openai_fails(monkeypatch):
    client = app.test_client()

    class DummyOpenAIFail:
        def analyze_free_text(self, *args, **kwargs):
            return {"success": False, "response": "", "error": "openai down"}

    class DummyClaude:
        def analyze_free_text(self, user_text, context="chatbot", history=None, active_major="", active_topic=""):
            assert user_text == "Em muốn hỏi thêm"
            return {
                "success": True,
                "response": "Claude fallback response",
                "source": "claude_fallback",
                "model": "test-claude",
            }

    monkeypatch.setattr("app.get_openai_fallback_api", lambda: DummyOpenAIFail())
    monkeypatch.setattr("app.get_claude_fallback_api", lambda: DummyClaude())

    response = client.post("/chat/fallback", json={"message": "Em muốn hỏi thêm"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["source"] == "claude_fallback"


def test_chat_fallback_endpoint_uses_last_fallback_when_openai_and_claude_fail(monkeypatch):
    client = app.test_client()

    class DummyOpenAIFail:
        def analyze_free_text(self, *args, **kwargs):
            return {"success": False, "response": "", "error": "openai down"}

    class DummyClaudeFail:
        def analyze_free_text(self, *args, **kwargs):
            return {"success": False, "response": "", "error": "claude down"}

    class DummyLastFallback:
        def analyze_free_text(self, user_text, context="chatbot", history=None, active_major="", active_topic=""):
            assert user_text == "Em muốn hỏi thêm"
            return {
                "success": True,
                "response": "Last fallback response",
                "source": "last_fallback_fallback",
                "model": "gpt-5.4",
            }

    monkeypatch.setattr("app.get_openai_fallback_api", lambda: DummyOpenAIFail())
    monkeypatch.setattr("app.get_claude_fallback_api", lambda: DummyClaudeFail())
    monkeypatch.setattr("app.get_last_fallback_api", lambda: DummyLastFallback())

    response = client.post("/chat/fallback", json={"message": "Em muốn hỏi thêm"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["source"] == "last_fallback_fallback"


def test_chat_fallback_endpoint_requires_message():
    client = app.test_client()
    response = client.post("/chat/fallback", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_chat_endpoint_should_not_reuse_stale_session_major_for_vague_major_choice(monkeypatch):
    client = app.test_client()

    class DummyChatbot:
        def __init__(self, predictor):
            self.predictor = predictor

        def _find_major_in_text(self, text):
            return ""

        def _is_followup_question(self, text):
            return False

        def _extract_context_major(self, history, current_message=""):
            return ""

        def _detect_followup_topic(self, text):
            return ""

        def chat(self, user_message, history=None, active_major=None, active_topic=None, feedback_data=None):
            assert user_message == "Em muốn thi đâu thi học ngành nào"
            assert active_major == ""
            assert active_topic == ""
            return {
                "reply": "Mình cần thêm thông tin để tư vấn đúng ngành.",
                "source": "context_clarify",
                "confidence": 0.3,
                "resolved_major": "",
                "resolved_topic": "major_selection",
                "needs_clarification": True,
            }

    monkeypatch.setattr("app.MajorChatbot", DummyChatbot)

    with client.session_transaction() as sess:
        sess["active_major"] = "Ky thuat xay dung"
        sess["active_topic"] = "overview"
        sess["chat_history"] = [
            {"role": "user", "content": "Cho em biết về ngành Kỹ thuật xây dựng"},
            {"role": "assistant", "content": "Ngành này liên quan đến công trình."},
        ]

    response = client.post(
        "/chat",
        json={
            "message": "Em muốn thi đâu thi học ngành nào",
            "history": [],
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["source"] == "context_clarify"
    assert payload["needs_clarification"] is True

    with client.session_transaction() as sess:
        assert sess.get("active_major", "") == ""
        assert sess.get("active_topic", "") == ""


def test_predict_should_not_call_fallback_when_form_values_match_labels(monkeypatch):
    client = app.test_client()

    class DummyPredictor:
        major_names = ["Marketing", "Quan tri kinh doanh", "Cong nghe thong tin"]

        def predict(self, payload):
            assert payload["so_thich_chinh"] == "du lich"
            return {
                "top_3": [
                    {"nganh": "Marketing", "score": 70.0, "absolute_score": 70.0, "raw_score": 70.0, "feedback": "ok"},
                    {"nganh": "Quan tri kinh doanh", "score": 60.0, "absolute_score": 60.0, "raw_score": 60.0, "feedback": "ok"},
                    {"nganh": "Cong nghe thong tin", "score": 50.0, "absolute_score": 50.0, "raw_score": 50.0, "feedback": "ok"},
                ]
            }

    class ShouldNotBeCalledFallback:
        def analyze_free_text(self, *args, **kwargs):
            raise AssertionError("Fallback API should not be called for matched form labels")

    monkeypatch.setattr("app.model_manager.ensure_ready", lambda: True)
    monkeypatch.setattr("app.model_manager._predictor", DummyPredictor())
    monkeypatch.setattr("app.get_openai_fallback_api", lambda: ShouldNotBeCalledFallback())
    monkeypatch.setattr("app.get_claude_fallback_api", lambda: ShouldNotBeCalledFallback())
    monkeypatch.setattr("app.get_last_fallback_api", lambda: ShouldNotBeCalledFallback())

    response = client.post(
        "/predict",
        json={
            "so_thich_chinh": "Du lịch",
            "mon_hoc_yeu_thich": "Anh",
            "ky_nang_noi_bat": "Thuyết trình",
            "tinh_cach": "Hướng ngoại",
            "moi_truong_lam_viec_mong_muon": "Linh hoạt",
            "muc_tieu_nghe_nghiep": "Theo đam mê",
            "mo_ta_ban_than": "Em thích giao tiếp và đi nhiều nơi.",
            "dinh_huong_tuong_lai": "Em muốn làm hướng dẫn viên du lịch.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fallback_used"] is False
    assert payload["fallback_meta"]["used"] is False


def test_predict_should_use_fallback_and_normalize_unmatched_form_values(monkeypatch):
    client = app.test_client()

    class DummyPredictor:
        major_names = ["Marketing", "Quan tri kinh doanh", "Cong nghe thong tin"]

        def predict(self, payload):
            # Sau fallback, payload phải map về nhãn hợp lệ rồi mới normalize qua row_dict_from_payload.
            assert payload["so_thich_chinh"] == "du lich"
            assert payload["ky_nang_noi_bat"] == "thuyet trinh"
            assert payload["moi_truong_lam_viec_mong_muon"] == "linh hoat"
            return {
                "top_3": [
                    {"nganh": "Huong dan du lich", "score": 82.0, "absolute_score": 82.0, "raw_score": 82.0, "feedback": "ok"},
                    {"nganh": "Du lich", "score": 74.0, "absolute_score": 74.0, "raw_score": 74.0, "feedback": "ok"},
                    {"nganh": "Marketing", "score": 61.0, "absolute_score": 61.0, "raw_score": 61.0, "feedback": "ok"},
                ]
            }

    class DummyOpenAIForFormFallback:
        def analyze_free_text(self, user_text, context="chatbot", history=None, active_major="", active_topic=""):
            assert context == "form"
            assert "normalized_fields" in user_text
            return {
                "success": True,
                "response": (
                    '{"normalized_fields": {'
                    '"so_thich_chinh": "Du lịch", '
                    '"mon_hoc_yeu_thich": "Anh", '
                    '"ky_nang_noi_bat": "Thuyết trình", '
                    '"tinh_cach": "Hướng ngoại", '
                    '"moi_truong_lam_viec_mong_muon": "Linh hoạt", '
                    '"muc_tieu_nghe_nghiep": "Theo đam mê"}, '
                    '"confidence": 0.91}'
                ),
                "source": "openai_fallback",
            }

    monkeypatch.setattr("app.model_manager.ensure_ready", lambda: True)
    monkeypatch.setattr("app.model_manager._predictor", DummyPredictor())
    monkeypatch.setattr("app.get_openai_fallback_api", lambda: DummyOpenAIForFormFallback())

    response = client.post(
        "/predict",
        json={
            "so_thich_chinh": "Khám phá",
            "mon_hoc_yeu_thich": "Anh",
            "ky_nang_noi_bat": "Nói chuyện trước đám đông",
            "tinh_cach": "Hướng ngoại",
            "moi_truong_lam_viec_mong_muon": "Di chuyển nhiều",
            "muc_tieu_nghe_nghiep": "Theo đam mê",
            "mo_ta_ban_than": "Em thích giao tiếp và đi nhiều nơi.",
            "dinh_huong_tuong_lai": "Em muốn làm hướng dẫn viên du lịch.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fallback_used"] is True
    assert payload["fallback_meta"]["used"] is True
    assert payload["fallback_meta"]["source"] == "openai"
    assert payload["fallback_meta"]["confidence"] == 0.91
    assert "so_thich_chinh" in payload["fallback_meta"]["changed_fields"]
