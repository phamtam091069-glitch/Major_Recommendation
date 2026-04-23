# 📖 Usage Guide: Updated app.py with ModelManager

## Khởi động ứng dụng

### 1. Chuẩn bị môi trường

```bash
# Vào thư mục dự án
cd major-recommendation

# Kích hoạt virtual environment
venv\Scripts\activate

# Cài đặt dependencies (nếu chưa)
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
# Phương pháp thông thường
python app.py

# Hoặc với Flask CLI
flask run
```

Output mong đợi:

```
INFO:app:✓ Model loaded successfully
 * Running on http://127.0.0.1:5000
```

---

## 📡 API Endpoints

### 1. **GET /** - Form chính

```bash
curl http://127.0.0.1:5000/
```

- Trả về HTML form
- Kiểm tra `model_ready` và `model_error`

### 2. **GET /health** - Health check

```bash
curl http://127.0.0.1:5000/health
```

**Response (Model ready):**

```json
{
  "status": "ok",
  "model_ready": true,
  "error": null
}
```

**Response (Model failed):**

```json
{
  "status": "ok",
  "model_ready": false,
  "error": "Thieu model: rf_model.pkl, ohe.pkl, ..."
}
```

### 3. **POST /predict** - Dự đoán ngành

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "so_thich_chinh": "cong nghe",
    "mon_hoc_yeu_thich": "toan",
    "ky_nang_noi_bat": "phan tich",
    "tinh_cach": "huong noi",
    "moi_truong_lam_viec_mong_muon": "van phong",
    "muc_tieu_nghe_nghiep": "thu nhap cao",
    "mo_ta_ban_than": "yeu thich lap trinh",
    "dinh_huong_tuong_lai": "tro thanh developer"
  }'
```

**Response:**

```json
{
  "top_3": [
    {
      "major": "Công nghệ thông tin",
      "score": 85.42,
      "score_fit": 85.42,
      "confidence": "Cao",
      "confidence_score": 82.1,
      "feedback": "Bạn có mức phù hợp cao với ngành Công nghệ thông tin.",
      "suggestion": "Xây dựng dự án lập trình thực tế..."
    },
    ...
  ]
}
```

---

## 🔍 Logging & Debugging

### Xem log messages

Log được in ra console khi:

- Model load thành công: `✓ Model loaded successfully`
- Model load thất bại: `✗ Failed to load model: ...`
- Model reload: `✓ Model reloaded successfully`
- Prediction error: `Prediction error: ...`
- Server error: `Internal server error: ...`

### Cấu hình log level

```python
import logging
import os

# Từ environment variable
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=LOG_LEVEL)
```

Ví dụ chạy với DEBUG level:

```bash
LOG_LEVEL=DEBUG python app.py
```

### Xem chi tiết lỗi

Khi model không load được, check `/health`:

```bash
curl http://127.0.0.1:5000/health | python -m json.tool
```

---

## 🧪 Testing

### Import ModelManager

```python
from app import model_manager

# Kiểm tra trạng thái
print(model_manager.is_ready)  # True/False
print(model_manager.error_message)  # "" hoặc error message

# Lấy predictor
if model_manager.is_ready:
    result = model_manager.predictor.predict(data)
```

### Unit test ví dụ

```python
import pytest
from unittest.mock import patch, MagicMock
from app import ModelManager

class TestModelManager:
    def test_init_success(self):
        """Test khởi tạo thành công."""
        with patch('app.load_predictor') as mock_load:
            mock_load.return_value = MagicMock()
            mgr = ModelManager()
            assert mgr.is_ready == True

    def test_init_failure(self):
        """Test khởi tạo thất bại."""
        with patch('app.load_predictor') as mock_load:
            mock_load.side_effect = FileNotFoundError("Model not found")
            mgr = ModelManager()
            assert mgr.is_ready == False
            assert "Model not found" in mgr.error_message

    def test_ensure_ready_reload(self):
        """Test reload model."""
        with patch('app.load_predictor') as mock_load:
            mock_load.return_value = MagicMock()
            mgr = ModelManager()

            # Simulate failure
            mgr._model_ready = False

            # Ensure ready should reload
            assert mgr.ensure_ready() == True
            assert mgr.is_ready == True
```

---

## 🛠️ Troubleshooting

### ❌ Error: "Model files missing"

**Giải pháp:**

```bash
# Train model lại
python train_model.py
```

### ❌ Error: "Vui long nhap day du cac truong bat buoc"

**Giải pháp:** Kiểm tra request JSON có tất cả 6 trường chọn:

- `so_thich_chinh`
- `mon_hoc_yeu_thich`
- `ky_nang_noi_bat`
- `tinh_cach`
- `moi_truong_lam_viec_mong_muon`
- `muc_tieu_nghe_nghiep`

Các trường tùy chọn (có thể trống):

- `mo_ta_ban_than`
- `dinh_huong_tuong_lai`

### ❌ Error: "Lỗi khi dự đoán"

**Debug:**

```bash
# Kiểm tra log
tail -f app.log

# Hoặc chạy server ở debug mode
python app.py --debug
```

### ❌ Port 5000 đang bị chiếm

**Giải pháp:**

```bash
# Chạy ở port khác
python app.py -p 8000
```

---

## 📊 Monitoring

### Check server status

```bash
# Health check
curl http://127.0.0.1:5000/health

# Hoặc dùng thư viện requests
python -c "
import requests
resp = requests.get('http://127.0.0.1:5000/health')
print(resp.json())
"
```

### Performance monitoring

Thêm tracking vào ModelManager (tương lai):

```python
class ModelManager:
    def __init__(self):
        self._prediction_count = 0
        self._total_time = 0.0

    @property
    def average_time(self):
        if self._prediction_count == 0:
            return 0.0
        return self._total_time / self._prediction_count
```

---

## 🔄 Cập nhật code

### Khi cần thay đổi ModelManager

1. **Không sửa global state** - EditMudelhass sử dụng properties
2. **Giữ backward compatibility** - Properties interface không đổi
3. **Test lại** - Chạy unit tests

Ví dụ thêm feature:

```python
class ModelManager:
    def get_prediction_count(self) -> int:
        """Lấy số lần predict."""
        return self._prediction_count  # ✅ Dùng property
```

---

## 📚 Tham khảo

- **REFACTOR_NOTES.md** - Chi tiết technical
- **IMPLEMENTATION_SUMMARY.md** - Tóm tắt thay đổi
- **README.md** - Tài liệu dự án gốc

---

**Last updated:** 2026-04-14
**Version:** 1.0
