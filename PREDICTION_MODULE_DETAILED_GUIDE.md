# 📊 SƠ ĐỒ CHI TIẾT MODULE PREDICTION

## 🎯 Tổng Quan Hệ Thống

Hệ thống AI tư vấn ngành học sử dụng một **Hybrid Prediction Model** kết hợp 3 thành phần chính:

1. **Model Score (30%)** - Điểm từ Machine Learning
2. **Criteria Score (40%)** - Điểm từ 8 tiêu chí minh bạch
3. **Rule Boost (30%)** - Điểm bổ sung từ phát hiện signals

---

## 📥 BƯỚC 1: DỮ LIỆU ĐẦU VÀO

### Trường Categorical (6 fields)

- **Sở thích chính** (interest) - Lựa chọn từ danh sách
- **Môn học yêu thích** (favorite_subject) - Lựa chọn từ danh sách
- **Tính cách** (personality) - Lựa chọn từ danh sách
- **Kỹ năng nổi bật** (skills) - Lựa chọn từ danh sách
- **Môi trường làm việc** (work_environment) - Lựa chọn từ danh sách
- **Mục tiêu nghề nghiệp** (career_goal) - Lựa chọn từ danh sách

### Trường Text (2 fields)

- **Mô tả bản thân** (self_description) - Văn bản tự do
- **Định hướng tương lai** (future_direction) - Văn bản tự do

---

## ⚙️ BƯỚC 2: FEATURE ENGINEERING

### One-Hot Encoding

- Chuyển 6 trường categorical thành vectors
- Mỗi giá trị được biểu diễn dưới dạng 0/1
- Kết quả: Feature vector kích thước cố định

### TF-IDF Vectorization

- Biến đổi 2 trường text thành numerical vectors
- Trích xuất các từ khóa quan trọng
- Tính toán tần suất từ trong toàn bộ corpus

### Kết Hợp Features

- Ghép One-Hot vectors + TF-IDF vectors
- Tạo ra Feature Vector hoàn chỉnh cho mô hình

---

## 📊 BƯỚC 3: TÍNH ĐIỂM (3 THÀNH PHẦN)

### 🤖 Model Score (30% weight)

**Thành phần 1: RandomForest Classifier**

- Mô hình: CalibratedRandomForest hoặc CalibratedLogisticRegression
- Đầu vào: Feature vectors (One-Hot + TF-IDF)
- Đầu ra: Probability scores cho mỗi ngành

**Thành phần 2: TF-IDF Cosine Similarity**

- So sánh hồ sơ học sinh với mô tả ngành
- Tính cosine similarity giữa vectors
- Kết quả: 0-1 (độ tương đồng)

**Công thức kết hợp:**

```
Model_Score = 0.60 × RF_Probability + 0.40 × Cosine_Similarity
Kết quả: 0-1
```

---

## 📐 BƯỚC 4: CRITERIA SCORE (40% weight)

### 8 Tiêu Chí Minh Bạch

| Tiêu chí                | Trọng số | Cách tính                  |
| ----------------------- | -------- | -------------------------- |
| 1. Sở thích chính       | 23%      | Match với sở thích ngành   |
| 2. Định hướng tương lai | 20%      | Khớp keywords trong text   |
| 3. Kỹ năng nổi bật      | 16%      | Match với kỹ năng cần      |
| 4. Tính cách            | 14%      | Phù hợp tính cách ngành    |
| 5. Môi trường làm việc  | 12%      | Match môi trường mong muốn |
| 6. Môn học yêu thích    | 8%       | Khớp nền tảng học tập      |
| 7. Mô tả bản thân       | 4%       | TF-IDF similarity          |
| 8. Mục tiêu nghề nghiệp | 3%       | Liên kết với ngành         |

**Công thức:**

```
Criteria_Score = Σ(Trọng số × Điểm khớp cho mỗi tiêu chí)
Kết quả: 0-100
```

---

## 🔧 BƯỚC 5: RULE BOOST (30% weight)

### Tech Signal Detection

Phát hiện 5 signals kỹ thuật:

1. Sở thích = "Công nghệ"
2. Môn học = "Tính toán" hoặc "Tin học"
3. Kỹ năng = "Phân tích dữ liệu" / "Tư duy logic"
4. Mục tiêu = "Phát triển chuyên môn" hoặc "Thu nhập cao"
5. Text chứa: "data", "dữ liệu", "phân tích", "data scientist"

**Nếu ≥ 3 signals:**

- Data Science boost: +18%
- IT boost: +11%
- Information Systems boost: +10%
- AI boost: +2%
- Software Development boost: +8%

### Language Signal Detection

Phát hiện 4 signals ngôn ngữ:

1. Sở thích = "Ngôn ngữ"
2. Môn học = "Anh"
3. Kỹ năng = "Giao tiếp" / "Thuyết trình"
4. Text chứa: "ngoại ngữ", "dịch", "văn hóa", "quốc tế"

**Nếu ≥ 2 signals:**

- Language majors boost: +20%

### Education Signal Detection

Nếu sở thích = "Giáo dục":

- Tất cả Sư phạm majors: +5%
- Sư phạm khớp môn học: +18%

---

## ⚡ BƯỚC 6: BLENDING SCORES

### Công Thức Cuối Cùng

```
Final_Score = 0.30 × Model_Score +
              0.70 × Criteria_Score +
              Rule_Boost

Kết quả: 0-100 (Điểm cuối cho mỗi ngành)
```

### Giải thích Trọng số

- **30% Model Score**: Dựa vào ML training
- **70% Criteria Score**: Luật minh bạch dễ giải thích
- **Rule Boost**: Tăng cường cho ngành được phát hiện

---

## 📊 BƯỚC 7: TẤT CẢ 15 NGÀNH

Lặp lại quy trình trên cho mỗi ngành:

1. Công nghệ thông tin
2. Khoa học dữ liệu
3. Quản trị kinh doanh
4. Marketing
5. Thiết kế đồ họa
6. Điều dưỡng
7. Ngôn ngữ Anh
8. Luật
9. Sư phạm
10. Hệ thống thông tin quản lý
11. Kế toán tài chính
12. Du lịch và lữ hành
13. Báo chí & truyền thông
14. Kiến trúc
15. Kỹ thuật cơ khí

---

## 🔢 BƯỚC 8: RANKING & TOP 3

### Quy Trình

1. **Sắp xếp** tất cả 15 ngành theo Final_Score (giảm dần)
2. **Chọn TOP 3** ngành có điểm cao nhất
3. **Tính Confidence Score** cho mỗi ngành

---

## 📈 BƯỚC 9: CONFIDENCE CALCULATION

### Công Thức Confidence

```
Confidence_Score =
  (TOP_1_Score - TOP_2_Score) × 100 +
  TOP_1_Score × 0.5

Thang: 0-100
```

### Nhãn Mức Độ Tin Cậy

- **Cao** (70+): Khá chắc chắn
- **Trung bình** (50-70): Có tham khảo giá trị
- **Tham khảo** (<50): Nên xem xét thêm các ngành khác

### Độ Tách Biệt (Confidence Note)

```
Gap = TOP_1_Score - TOP_4_Score

Hiển thị: "Chênh ngành kế tiếp: +X.XX điểm"
```

---

## ✅ BƯỚC 10: OUTPUT JSON

### Response Format

```json
{
  "top_3": [
    {
      "rank": 1,
      "major": "Công nghệ thông tin",
      "score": 82.5,
      "score_fit": 82.5,
      "score_relative": 100.0,
      "score_model": 0.78,
      "score_criteria": 85.0,
      "confidence_score": 75,
      "confidence": "Cao",
      "confidence_note": "Chênh ngành kế tiếp: +8.5 điểm",
      "feedback": "Bạn có mức phù hợp cao với ngành Công nghệ thông tin",
      "suggestion": "Bạn nên tập trung vào các kỹ năng lập trình..."
    },
    ...
  ]
}
```

### Các Trường Chính

- **major**: Tên ngành hiển thị cho người dùng
- **score**: Điểm cuối (0-100)
- **score_model**: Điểm từ ML component
- **score_criteria**: Điểm từ 8 tiêu chí
- **confidence_score**: Độ tin cậy (0-100)
- **confidence**: Nhãn: "Cao" / "Trung bình" / "Tham khảo"
- **suggestion**: Lời khuyên cá nhân hóa
- **feedback**: Giải thích về sự phù hợp

---

## 📤 BƯỚC 11: HIỂN THỊ UI

Frontend nhận JSON response và:

1. Hiển thị TOP 3 ngành
2. Vẽ progress bar với điểm score
3. Hiển thị Confidence badge
4. Dùng animated transitions

---

## 🔑 Các File Chính

| File                        | Mục đích                       |
| --------------------------- | ------------------------------ |
| `utils/predictor.py`        | Logic chính: scoring + ranking |
| `app.py`                    | Flask route `/predict`         |
| `templates/index.html`      | Form input                     |
| `static/script.js`          | Chuẩn hóa dữ liệu + gọi API    |
| `models/rf_model.pkl`       | Trained RandomForest           |
| `models/majors.json`        | Mô tả ngành + metadata         |
| `models/hybrid_config.json` | Cấu hình weights               |

---

## 💡 Key Points

✅ **Hybrid Approach**: Kết hợp ML (data-driven) + Rules (explainable)
✅ **Transparent**: 8 tiêu chí minh bạch giúp người dùng hiểu kết quả
✅ **Confidence Calibration**: Cung cấp mức độ tin cậy cho từng dự đoán
✅ **Signal Detection**: Tự động phát hiện ngành dựa trên patterns
✅ **Top-3 Format**: Cung cấp nhiều lựa chọn thay vì 1 kết quả duy nhất

---

**Generated:** April 21, 2026
**Version:** 1.0
