# 🎓 Hệ thống AI Tư Vấn Ngành Học Phù Hợp

[![GitHub Repository](https://img.shields.io/badge/GitHub-Major_Recommendation-blue)](https://github.com/phamtam091069-glitch/Major_Recommendation)
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()

Ứng dụng web **Flask** gợi ý **Top 3 ngành đại học** dựa trên hồ sơ học sinh (biểu mẫu + mô tả tự do). Phù hợp demo đồ án, tiểu luận hoặc mở rộng thêm dữ liệu thực tế.

**📍 GitHub Repository:** [https://github.com/phamtam091069-glitch/Major_Recommendation](https://github.com/phamtam091069-glitch/Major_Recommendation)

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
     - Sở thích chính: **23%**
     - Định hướng tương lai: **20%**
     - Kỹ năng nổi bật: **16%**
     - Tính cách: **14%**
     - Môi trường làm việc mong muốn: **12%**
     - Môn học yêu thích: **8%**
     - Mô tả bản thân: **4%**
     - Mục tiêu nghề nghiệp: **3%**

3. **Final score (điểm cuối hiển thị)**
   - Công thức đang dùng:
     - **60% model score + 40% criteria score**
   - 1 dòng công thức:
     - **FinalScore(ngành) = 0.60 × ModelScore(ngành) + 0.40 × CriteriaScore(ngành)**

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

## Danh sách ngành (73 ngành)

Hệ thống hỗ trợ **73 ngành đại học** phân loại theo các nhóm chính:

### 🏢 Các Nhóm Ngành Chính

| Nhóm                                              | Số Lượng | Ví Dụ Ngành                                                                                                                 |
| ------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Công nghệ - Kỹ thuật**                          | 15+      | Công nghệ thông tin, Khoa học dữ liệu, Kỹ thuật phần mềm, Kỹ thuật cơ khí, Hệ thống thông tin, Tự động hóa, ...             |
| **Kinh doanh - Tài chính - Quản trị**             | 15+      | Quản trị kinh doanh, Marketing, Kế toán tài chính, Kinh doanh quốc tế, Logistics, Quản lý khách sạn, ...                    |
| **Xã hội - Nhân văn - Giáo dục - Luật**           | 15+      | Sư phạm (Toán, Lý, Hóa, Sinh, Địa, Sử), Luật, Ngôn ngữ Anh, Ngôn ngữ Hán, Ngôn ngữ Nhật, Ngôn ngữ Trung, ...                |
| **Sức khỏe - Dịch vụ cộng đồng**                  | 12+      | Điều dưỡng, Y học, Dược học, Kỹ thuật xét nghiệm y học, Dinh dưỡng, Tâm lý học, ...                                         |
| **Sáng tạo - Truyền thông - Du lịch - Kiến trúc** | 15+      | Thiết kế đồ họa, Du lịch và lữ hành, Báo chí truyền thông, Kiến trúc, Thiết kế nội thất, Thiết kế thời trang, Mỹ thuật, ... |

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
  └─ Final score = 60% model + 40% criteria
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

## 🚀 Deployment

### PythonAnywhere (Khuyến nghị)

Xem hướng dẫn chi tiết: **`PYTHONANYWHERE_DEPLOYMENT_GUIDE.md`**

Quick start (5 phút):

1. Đăng ký: https://www.pythonanywhere.com
2. Upload code via Git clone
3. Tạo web app, config WSGI
4. Reload và truy cập URL public

### Replit

Xem hướng dẫn chi tiết: **`REPLIT_DEPLOYMENT_GUIDE.md`**

Quick start:

1. Import từ GitHub: https://github.com/phamtam091069-glitch/Major_Recommendation
2. Cài dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`
4. Truy cập link public Replit

## 📚 Tài Liệu Hướng Dẫn

Các file hướng dẫn trong project:

| File                                 | Mục Đích                           |
| ------------------------------------ | ---------------------------------- |
| `README.md`                          | Tổng quan project (file này)       |
| `GITHUB_SETUP_GUIDE.md`              | Cách setup GitHub account          |
| `PYTHONANYWHERE_QUICK_START.md`      | Deployment PythonAnywhere (5 phút) |
| `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` | Hướng dẫn PythonAnywhere chi tiết  |
| `REPLIT_QUICK_START.md`              | Deployment Replit (5 phút)         |
| `REPLIT_DEPLOYMENT_GUIDE.md`         | Hướng dẫn Replit chi tiết          |

## 🔗 GitHub Information

**Tài Khoản:** phamtam091069-glitch  
**Email:** phamtam091069@gmail.com  
**Repository:** https://github.com/phamtam091069-glitch/Major_Recommendation  
**Trạng Thái:** Public (có thể deploy trên Replit/PythonAnywhere)

### Cách Push Code Lên GitHub

```bash
# 1. Add remote (nếu chưa làm)
git remote add origin https://github.com/phamtam091069-glitch/Major_Recommendation.git

# 2. Rename branch
git branch -M main

# 3. Push code
git push -u origin main
```

### Cách Update Sau Khi Thay Đổi Code

```bash
# 1. Stage changes
git add .

# 2. Commit
git commit -m "Describe your changes"

# 3. Push to GitHub
git push origin main
```

## 🔧 Environment Variables

Tạo file `.env` trong thư mục project với các biến sau:

```env
# API Keys (optional - dùng cho fallback)
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Flask
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

## 📊 Project Statistics

- **Total Files:** 290+
- **Total Lines of Code:** 99,800+
- **Languages:** Python, JavaScript, HTML, CSS
- **ML Models:** CalibratedRandomForest, CalibratedLogisticRegression
- **Major Classes:** 73 ngành học
- **Endpoints:** 8 API endpoints
- **Support Categories:** 5 nhóm ngành chính

## 🎯 Architecture Overview

### Technology Stack

- **Backend:** Flask (Python 3.10+)
- **ML:** scikit-learn (Random Forest, Logistic Regression)
- **Text Processing:** TF-IDF, cosine similarity
- **Data:** pandas, numpy
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

### Key Components

1. **`app.py`** - Flask application & API endpoints
2. **`utils/predictor.py`** - ML model & scoring logic
3. **`utils/chatbot.py`** - AI chatbot functionality
4. **`train_model.py`** - Model training pipeline
5. **`templates/index.html`** - Main form UI
6. **`static/script.js`** - Frontend logic & data normalization

## 🐛 Troubleshooting

### Model Not Loading

```bash
# Retrain model
python train_model.py
```

### Data Format Issues

```bash
# Check & clean data
python data/audit_dataset.py
```

### Text Encoding Problems

- Frontend automatically normalizes Vietnamese diacritics
- Check `static/script.js` for normalization logic

## 📝 Ghi Chú

- Dữ liệu synthetic có thể cho metric cao nhưng không phản ánh hoàn toàn dữ liệu thực tế.
- Khi sửa dữ liệu hoặc logic chấm điểm, nên train lại bằng `python train_model.py`.
- Kiểm tra nhanh trạng thái model bằng `GET /health`.
- Git history được lưu tự động, có thể revert thay đổi nếu cần.

## 📞 Support & Contribution

- Repository: https://github.com/phamtam091069-glitch/Major_Recommendation
- Issues & PRs: Chào mừng các đóng góp!
- Contact: phamtam091069@gmail.com

---

**Last Updated:** April 24, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
