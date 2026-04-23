# 🔄 Refactor Notes: Model State Management

## Tóm tắt thay đổi

Refactor file `app.py` để **loại bỏ `global` variables** và sử dụng **class-based approach** (`ModelManager`) để quản lý model state một cách sạch sẽ, an toàn và dễ bảo trì hơn.

---

## 🔴 Vấn đề cũ (Trước refactor)

### Global Variables

```python
try:
    predictor = load_predictor()
    MODEL_READY = True
    MODEL_ERROR = ""
except Exception as exc:
    predictor = None
    MODEL_READY = False
    MODEL_ERROR = str(exc)
```

**Nhược điểm:**

- ❌ Sử dụng `global` trong hàm `predict()` có thể gây nhầm lẫn
- ❌ Khó theo dõi state thay đổi
- ❌ Không thread-safe trong multi-threaded environment
- ❌ Khó test và mock model
- ❌ Dễ xảy ra race condition

---

## 🟢 Giải pháp mới (Sau refactor)

### Class `ModelManager`

```python
class ModelManager:
    """Quản lý model state một cách sạch sẽ (thay thế global variables)."""

    def __init__(self):
        self._predictor: Optional[Predictor] = None
        self._model_ready: bool = False
        self._model_error: str = ""
        self._initialize_model()

    def ensure_ready(self) -> bool:
        """Đảm bảo model sẵn sàng, thử load lại nếu cần."""
        ...

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
```

**Lợi ích:**

- ✅ Encapsulation: State được quản lý bên trong class
- ✅ Type hints rõ ràng
- ✅ Properties giúp access state an toàn
- ✅ Dễ mở rộng và test
- ✅ Rõ ràng hơn, dễ đọc

---

## 📋 Chi tiết thay đổi

### 1. **Thêm Logging**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

- Giúp debug và monitor ứng dụng
- Có thể config log level từ environment variable

### 2. **Tách hàm `load_feedback_data()`**

**Trước:** Load feedback data trực tiếp ở module level
**Sau:** Tách thành hàm, gọi theo nhu cầu

```python
def load_feedback_data() -> dict:
    """Load dữ liệu phản hồi từ file JSON."""
    try:
        with FEEDBACK_DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning(f"Không load được feedback data: {exc}")
        return {}
```

- Giảm overhead lúc startup
- Reload data mà không cần restart server

### 3. **Tách hàm `format_top3_results()`**

**Trước:** Logic format nhúng trong hàm `predict()`
**Sau:** Tách thành hàm riêng

```python
def format_top3_results(results: list, feedback_data: dict) -> list:
    """Format kết quả top 3 từ model."""
    ...
```

- Dễ test unit test riêng
- Reusable nếu cần format ở endpoint khác
- Code `predict()` sạch sẽ hơn

### 4. **ModelManager: Singleton-like pattern**

```python
model_manager = ModelManager()
```

- Khởi tạo một instance duy nhất (tương tự Flask app)
- Sử dụng `model_manager.is_ready`, `model_manager.predictor` thay vì global variables

### 5. **Health endpoint cải thiện**

**Trước:**

```python
@app.route("/health")
def health():
    return jsonify({"status": "ok", "model_ready": MODEL_READY})
```

**Sau:**

```python
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_ready": model_manager.is_ready,
        "error": model_manager.error_message if not model_manager.is_ready else None,
    })
```

- Thêm error message nếu model không ready

### 6. **Error handlers**

```python
@app.errorhandler(404)
def not_found(error):
    """Xử lý 404 errors."""
    return jsonify({"error": "Endpoint không tồn tại"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Xử lý 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Lỗi server nội bộ"}), 500
```

- Consistent error responses
- Logging errors cho debugging

---

## 🧪 Testing

### Cách test ModelManager:

```python
from unittest.mock import patch
from app import ModelManager

def test_model_manager_init():
    """Test khởi tạo ModelManager."""
    with patch('app.load_predictor') as mock_load:
        mock_load.return_value = MagicMock()
        mgr = ModelManager()
        assert mgr.is_ready == True

def test_model_manager_ensure_ready():
    """Test ensure_ready khi model fail."""
    mgr = ModelManager()
    mgr._model_ready = False

    with patch('app.load_predictor') as mock_load:
        mock_load.return_value = MagicMock()
        assert mgr.ensure_ready() == True
```

---

## 📊 So sánh

| Yếu tố               | Trước                                         | Sau                        |
| -------------------- | --------------------------------------------- | -------------------------- |
| **Global variables** | 3 (`predictor`, `MODEL_READY`, `MODEL_ERROR`) | 0                          |
| **State management** | Module-level (implicit)                       | Class-based (explicit)     |
| **Thread-safety**    | Kém                                           | Tốt hơn (nếu thêm locking) |
| **Testability**      | Khó                                           | Dễ (có thể mock)           |
| **Error logging**    | Không có                                      | Có chi tiết                |
| **Code clarity**     | Trung bình                                    | Tốt                        |
| **Lines of code**    | 164                                           | 260 (nhưng organized hơn)  |

---

## 🚀 Cách sử dụng

**Cũ:**

```python
# file_any_place.py
from app import predictor, MODEL_READY
```

**Mới:**

```python
# file_any_place.py
from app import model_manager

if model_manager.is_ready:
    result = model_manager.predictor.predict(data)
```

---

## 📝 Lợi ích dài hạn

1. **Bảo trì dễ hơn** - Code rõ ràng, dễ hiểu
2. **Mở rộng dễ** - Thêm features mới không ảnh hưởng state
3. **Debug dễ** - Logging giúp track lỗi
4. **Test dễ** - Có thể mock ModelManager
5. **Production-ready** - Error handling đầy đủ
6. **Scalable** - Nền tảng tốt cho deployment

---

## 💡 Đề xuất cải thiện tương lai

1. **Thêm mutex lock** cho thread-safety:

```python
from threading import Lock

class ModelManager:
    def __init__(self):
        self._lock = Lock()
        ...

    def ensure_ready(self) -> bool:
        with self._lock:
            # load model
```

2. **Thêm caching** cho feedback data:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_feedback_data() -> dict:
    ...
```

3. **Environment variables** cho config:

```python
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=LOG_LEVEL)
```

4. **Metrics/Monitoring** cho model usage:

```python
class ModelManager:
    def __init__(self):
        self._prediction_count = 0

    def predict(self, data):
        self._prediction_count += 1
        return self.predictor.predict(data)
```

---

## ✅ Checklist

- [x] Loại bỏ `global` variables
- [x] Tạo `ModelManager` class
- [x] Tách hàm logic
- [x] Thêm logging
- [x] Thêm error handlers
- [x] Code compile thành công
- [ ] Unit tests (đề xuất)
- [ ] Integration tests (đề xuất)

---

**Created:** 2026-04-14  
**Author:** Cline AI Assistant  
**Status:** Completed ✓
