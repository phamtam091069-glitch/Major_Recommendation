# Hệ thống AI tư vấn ngành học phù hợp

Ứng dụng web **Flask** gợi ý **Top 3 ngành đại học** dựa trên hồ sơ học sinh (biểu mẫu + mô tả tự do). Phù hợp demo đồ án, tiểu luận hoặc mở rộng thêm dữ liệu thực tế.

## Đầu vào người dùng

| Nhóm                        | Trường                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Bắt buộc                    | Sở thích chính, môn học yêu thích, kỹ năng nổi bật, tính cách, môi trường làm việc mong muốn, mục tiêu nghề nghiệp |
| Tùy chọn (khuyến nghị điền) | Mô tả bản thân, định hướng tương lai                                                                               |

Frontend chuẩn hóa tiếng Việt có dấu sang dạng **không dấu** trước khi gửi API để khớp dữ liệu huấn luyện (`static/script.js`).

## Cách hoạt động hiện tại (Hybrid + Explainable)

Hệ thống không dùng một model đơn lẻ, mà kết hợp nhiều lớp điểm:

1. **Model score (điểm mô hình)**
   - Model phân loại đã train và lưu trong `models/rf_model.pkl`.
   - Có thể là **CalibratedRandomForest** hoặc **CalibratedLogisticRegression** (được chọn theo chất lượng khi train).
   - Đầu vào model: **One-Hot categorical** + **TF-IDF text profile**.
   - Kết hợp nội bộ trong predictor:
     - xác suất học máy (ML probability)
     - cosine similarity giữa hồ sơ học sinh và mô tả ngành
     - rule boost nhẹ (đã giới hạn để không lấn model)

2. **Criteria score (điểm tiêu chí minh bạch theo 8 trường)**
   - Chấm điểm theo trọng số cố định:
     - Sở thích chính: **18%**
     - Môn học yêu thích: **12%**
     - Kỹ năng nổi bật: **15%**
     - Tính cách: **10%**
     - Môi trường làm việc mong muốn: **10%**
     - Mục tiêu nghề nghiệp: **10%**
     - Mô tả bản thân: **15%**
     - Định hướng tương lai: **10%**

3. **Final score (điểm cuối hiển thị)**
   - Công thức đang dùng:
     - **70% model score + 30% criteria score**
   - 1 dòng công thức:
     - **FinalScore(ngành) = 0.70 × ModelScore(ngành) + 0.30 × CriteriaScore(ngành)**

> `score` hiển thị trong UI là điểm cuối (0-100).  
> `score_relative` chỉ dùng để so sánh tỉ lệ giữa các ngành trong cùng một lượt dự đoán.

## Độ tin cậy (Confidence)

API trả thêm độ tin cậy theo thang 0-100:

- Dựa trên **fit score của ngành** + **độ tách biệt với ngành kế tiếp**.
- Hiển thị kèm nhãn:
  - Cao
  - Trung bình
  - Tham khảo

UI hiển thị dạng:

- `Độ tin cậy: 78/100 (Cao) · Chênh ngành kế tiếp: +0.0123 điểm thô`

## Danh sách ngành (15 lớp)

Nhãn dùng trong dữ liệu/model:

- Công nghệ thông tin, Khoa học dữ liệu, Quản trị kinh doanh, Marketing, Thiết kế đồ họa
- Điều dưỡng, Ngôn ngữ Anh, Luật, Sư phạm, Hệ thống thông tin quản lý
- Kế toán tài chính, Du lịch và lữ hành, Báo chí và truyền thông, Kiến trúc, Kỹ thuật cơ khí

JSON trả về có `top_3[].nganh` theo nhãn model (không dấu), ví dụ: `Ke toan tai chinh`, `Du lich va lu hanh`.

## Cài đặt môi trường

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Dữ liệu huấn luyện

Bạn có thể tạo lại dữ liệu cân bằng:

```bash
python data/generate_balanced_students.py
```

Chỉnh số mẫu mỗi ngành bằng `ROWS_PER_MAJOR` trong `data/generate_balanced_students.py`.

## Audit chất lượng dữ liệu

```bash
python data/audit_dataset.py
```

Sinh báo cáo:

- `reports/data_audit.txt`
- `reports/data_audit.json`

Quy trình khuyến nghị:

1. `python data/audit_dataset.py`
2. Làm sạch `data/raw/students.csv` nếu cần
3. `python train_model.py`
4. So sánh `reports/evaluation.txt` trước/sau
5. Kiểm tra `reports/confusion_matrix.csv`

## Huấn luyện model

```bash
python train_model.py
```

Sinh / cập nhật:

- `models/rf_model.pkl`, `ohe.pkl`, `tfidf.pkl`, `classes.pkl`
- `models/majors.json`
- `models/hybrid_config.json` (weight + model được chọn)
- `reports/evaluation.txt`
- `reports/confusion_matrix.csv`
- `reports/per_class_metrics.csv`

Sau khi train, chạy lại `python app.py` để nạp model mới.

## Chạy ứng dụng web

```bash
python app.py
```

Truy cập: `http://127.0.0.1:5000`

## API nhanh

| Method | Endpoint   | Mô tả                                          |
| ------ | ---------- | ---------------------------------------------- |
| GET    | `/`        | Trang form                                     |
| GET    | `/health`  | `{ "status", "model_ready" }`                  |
| POST   | `/predict` | Nhận JSON hồ sơ, trả Top 3 + điểm + giải thích |

Một item trong `top_3` hiện có các trường chính:

- `major`: tên ngành hiển thị
- `score`: điểm cuối (0-100)
- `score_fit`: điểm fit để hiển thị
- `score_relative`: tỉ lệ trong lượt dự đoán
- `score_model`: điểm từ model
- `score_criteria`: điểm từ 8 tiêu chí minh bạch
- `confidence_score`, `confidence`, `confidence_note`
- `feedback`, `suggestion`

## Sơ đồ luồng xử lý

```text
[Người dùng nhập form]
        |
        v
templates/index.html + static/script.js
(chuẩn hóa dữ liệu, gọi POST /predict)
        |
        v
app.py (/predict)
(validate input + gọi predictor)
        |
        v
utils/predictor.py
  ├─ OneHot(6 trường chọn)
  ├─ TF-IDF(2 trường text)
  ├─ Model score (ML + cosine + rule boost nhẹ)
  ├─ Criteria score (8 tiêu chí minh bạch)
  └─ Final score = 70% model + 30% criteria
        |
        v
app.py format response
(major hiển thị, confidence, suggestion)
        |
        v
JSON trả về frontend
(top_3 + điểm + giải thích)
        |
        v
static/script.js render UI
(progress, confidence, feedback)
```

### Luồng train model (offline)

```text
data/raw/students.csv
        |
        v
train_model.py
  ├─ train + calibration + chọn model tốt hơn
  ├─ lưu models/*.pkl + hybrid_config.json
  └─ xuất reports/evaluation.txt, confusion_matrix.csv...
        |
        v
app.py load artifact mới khi khởi động lại
```

## Cấu trúc thư mục

```text
major-recommendation/
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── data/
│   ├── generate_balanced_students.py
│   ├── audit_dataset.py
│   └── raw/
│       └── students.csv
├── models/
├── utils/
│   ├── predictor.py
│   ├── features.py
│   └── constants.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── reports/
└── tests/
```

## Ghi chú

- Dữ liệu synthetic có thể cho metric cao nhưng không phản ánh hoàn toàn dữ liệu thực tế.
- Khi sửa dữ liệu hoặc logic chấm điểm, nên train lại bằng `python train_model.py`.
- Kiểm tra nhanh trạng thái model bằng `GET /health`.
