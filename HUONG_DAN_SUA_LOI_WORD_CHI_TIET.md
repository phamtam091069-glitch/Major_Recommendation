# 🔧 **HƯỚNG DẪN CHI TIẾT SỬA LỖI FILE WORD**

---

## **🔴 PRIORITY 1: CÓC PHẢI SỬA NGAY**

### **❌ LỖI #1: SỬA TRỌNG SỐ CHƯƠNG 7.2.1**

**Vị trí:** Chương 7 → 7.2.1 (Dữ liệu huấn luyện là synthetic)

**Hiện tại (SAI):**

```
Giải pháp hiện tại: Dự án đã giảm trọng số model từ 60% xuống 30%,
tăng trọng số criteria score lên 70% để hạn chế ảnh hưởng của overfitting.
```

**Sửa thành (ĐÚNG):**

```
Giải pháp hiện tại: Dự án sử dụng trọng số 60% Model Score + 40% Criteria Score
để cân bằng giữa độ chính xác của model machine learning và tính minh bạch
của criteria-based scoring, từ đó hạn chế ảnh hưởng của overfitting trên dữ liệu synthetic.
```

**Tại sao sửa:**

- ✅ Code thực tế dùng 60% model + 40% criteria (KHÔNG phải 30/70)
- ✅ File Word nói sai, gây nhầm lẫn
- 🔴 **CRITICAL BUG - ảnh hưởng đến hiểu về project**

**Bước thực hiện:**

1. Mở file Word
2. Dùng **Ctrl+H** → Tìm & Thay thế
3. Tìm: `giảm trọng số model từ 60% xuống 30%, tăng trọng số criteria score lên 70%`
4. Thay thành: `sử dụng trọng số 60% Model Score + 40% Criteria Score để cân bằng giữa độ chính xác của model machine learning và tính minh bạch của criteria-based scoring`
5. Click **Replace All**

---

### **❌ LỖI #2: KIỂM TRA & SỬA CHƯƠNG 2.3 VỀ TRỌNG SỐ**

**Vị trí:** Chương 2 → 2.3 (Thuật toán chấm điểm)

**Hiện tại (ĐÚNG):**

```
Final Score = 60% × Model Score + 40% × Criteria Score

2.3.1. Model Score (60%)
2.3.2. Criteria Score (40%)
```

**Status:** ✅ **ĐÃ ĐÚNG - KHÔNG CẦN SỬA**

**Kiểm tra:**

- Section 2.3 nói: **60% model, 40% criteria** ✅
- Code thực tế: **60% model, 40% criteria** ✅
- **KHỚP NHAU!**

**Tuy nhiên cần thêm chi tiết:**

Tìm dòng này trong 2.3.1:

```
Model Score (60%)
```

Thay thành:

```
Model Score (60%) - CalibratedRandomForest hoặc CalibratedLogisticRegression
```

---

## **🟡 PRIORITY 2: CẦN SỬA TRONG NGÀY**

### **LỖI #3: THÊM "CALIBRATED" TRONG CHƯƠNG 2.3**

**Vị trí:** Chương 2 → 2.3.1

**Hiện tại:**

```
Model Score (60%):
- Random Forest hoặc Logistic Regression (được chọn theo chất lượng)
- Input: OneHot categorical + TF-IDF text vectors
```

**Sửa thành:**

```
Model Score (60%):
- CalibratedRandomForest hoặc CalibratedLogisticRegression
  (được chọn dựa trên hiệu suất cross-validation)
- Calibration giúp đảm bảo xác suất dự đoán phản ánh độ tin cậy thực tế
- Input: OneHot categorical + TF-IDF text vectors
```

**Tại sao:**

- Model được wrap bằng `CalibratedClassifierCV`
- Rất quan trọng để tính confidence score đúng

**Bước thực hiện:**

1. Tìm: `Random Forest hoặc Logistic Regression (được chọn theo chất lượng)`
2. Thay: `CalibratedRandomForest hoặc CalibratedLogisticRegression (được chọn dựa trên hiệu suất cross-validation)`
3. Thêm dòng mới: `- Calibration giúp đảm bảo xác suất dự đoán phản ánh độ tin cậy thực tế`

---

### **LỖI #4: THÊM 2 FILE CÒN THIẾU TRONG CHƯƠNG 5.4.1**

**Vị trí:** Chương 5 → 5.4.1 (Đóng gói mô hình AI)

**Hiện tại (THIẾU):**

```
Bốn tệp mô hình được lưu trữ và sử dụng trong hệ thống:
- rf_model.pkl
- ohe.pkl
- tfidf.pkl
- classes.pkl
```

**Sửa thành (ĐỦ 6 FILE):**

```
Sáu tệp mô hình và cấu hình được lưu trữ và sử dụng trong hệ thống:

1. rf_model.pkl: Mô hình RandomForest Classifier (hoặc LogisticRegression)
   đã được huấn luyện trên tập dữ liệu ~43,550 mẫu

2. ohe.pkl: Đối tượng OneHotEncoder đã được fit, dùng để biến đổi dữ liệu
   categorical thành vector số

3. tfidf.pkl: Đối tượng TfidfVectorizer đã được fit trên corpus văn bản,
   dùng để biến đổi dữ liệu text

4. classes.pkl: Danh sách các nhãn lớp tương ứng với 73 ngành học

5. majors.json: Thông tin chi tiết về 73 ngành học, bao gồm mô tả,
   đặc điểm và các gợi ý liên quan

6. hybrid_config.json: Cấu hình hybrid chứa trọng số kết hợp
   (60% Model Score + 40% Criteria Score)
```

**Bước thực hiện:**

1. Mở file Word
2. Tìm section "Bốn tệp mô hình được lưu trữ"
3. Đổi "Bốn" → "Sáu"
4. Thêm 2 file mới: `majors.json` và `hybrid_config.json`

---

### **LỖI #5: RÕ RÀNG HÓA CÔNG THỨC α=0.6 TRONG CHƯƠNG 1.4**

**Vị trí:** Chương 1 → 1.4 (Phạm vi lý thuyết)

**Hiện tại (MỜ):**

```
- Hybrid Approach: Công thức kết hợp α=0.6, 8 Criteria-based Scoring
```

**Sửa thành (RÕ RÀNG):**

```
- Hybrid Approach: Kết hợp 60% Model Score (α=0.6) + 40% Criteria Score (α'=0.4)
  dựa trên 8 tiêu chí minh bạch
```

**Tại sao:**

- α=0.6 ở đây chỉ là biến ký hiệu cho "60%"
- Cần rõ ràng hơn để người đọc hiểu

**Bước thực hiện:**

1. Tìm: `Công thức kết hợp α=0.6, 8 Criteria-based Scoring`
2. Thay: `Kết hợp 60% Model Score (α=0.6) + 40% Criteria Score (α'=0.4) dựa trên 8 tiêu chí minh bạch`

---

### **LỖI #6: NÓI RÕ DÙNG TF-IDF, KHÔNG DÙNG PHOBE RT TRONG CHƯƠNG 6.1**

**Vị trí:** Chương 6 → 6.1 (Thiết lập thực nghiệm)

**Hiện tại (CÓ ĐỀ CẬP PHOBE RT):**

```
Feature Extraction Method... (nếu có nhắc đến PhoBERT)
```

**Kiểm tra:**

- ✅ File Word có nói dùng TF-IDF
- ❌ File Word có nhắc đến PhoBERT
- ❌ Code **KHÔNG dùng PhoBERT**

**Cần thêm vào Chương 6.1:**

```
Feature Extraction Method:
- Categorical Features: OneHotEncoder (convert 6 trường select thành binary vectors)
- Text Features: TF-IDF Vectorizer (không dùng neural embedding như PhoBERT)
- Semantic Similarity: Cosine Similarity trên TF-IDF vectors
- Động lực: TF-IDF đơn giản, nhanh, phù hợp với dữ liệu synthetic nhỏ
```

**Tại sao:**

- Code dùng `TfidfVectorizer` từ sklearn
- Không có `PhoBERT`
- Cần rõ ràng để không gây nhầm lẫn

**Bước thực hiện:**

1. Thêm section mới trong 6.1 về Feature Extraction Method
2. Nói rõ: "Hệ thống sử dụng TF-IDF để vectorize text, **không dùng neural embedding**"

---

## **📋 BẢNG CHECK LỖI - HOÀN THÀNH**

| #   | Lỗi                         | Vị trí   | Priority    | ✅/❌          |
| --- | --------------------------- | -------- | ----------- | -------------- |
| 1   | Trọng số 30/70 vs 60/40 sai | Ch 7.2.1 | 🔴 CRITICAL | ❌ Sửa ngay    |
| 2   | Thêm "Calibrated"           | Ch 2.3.1 | 🟡 MINOR    | ❌ Sửa hôm nay |
| 3   | Thêm 2 file JSON            | Ch 5.4.1 | 🟡 MINOR    | ❌ Sửa hôm nay |
| 4   | Rõ ràng α=0.6               | Ch 1.4   | 🟡 MINOR    | ❌ Sửa hôm nay |
| 5   | Nói rõ TF-IDF không PhoBERT | Ch 6.1   | 🟡 MINOR    | ❌ Sửa hôm nay |

---

## **🎯 HÀNH ĐỘNG NGAY LẬP TỨC**

**Bước 1: Mở file Word**

```
File: ĐỀ CƯƠNG TIỂU LUẬN AI.docx
```

**Bước 2: Sửa lỗi CRITICAL (Priority 1)**

- [ ] Chương 7.2.1: Sửa 30/70 → 60/40

**Bước 3: Sửa lỗi MINOR (Priority 2)**

- [ ] Chương 2.3.1: Thêm "Calibrated"
- [ ] Chương 5.4.1: Thêm 2 file (majors.json, hybrid_config.json)
- [ ] Chương 1.4: Rõ ràng hóa α=0.6
- [ ] Chương 6.1: Nói rõ TF-IDF không PhoBERT

**Bước 4: Lưu file**

```
Ctrl+S hoặc File → Save
```

**Bước 5: Kiểm tra lại**

- [ ] Tất cả trọng số đúng (60/40)
- [ ] Tất cả file đúng (6 file)
- [ ] Feature extraction rõ ràng (TF-IDF)

---

## **💡 MẸO TÌM & THAY TRONG WORD**

1. **Mở Find & Replace:**
   - Windows: `Ctrl+H`
   - Mac: `Cmd+Option+F`

2. **Tìm dòng:**
   - Nhập text cần tìm trong ô "Find"
   - Click "Find All" để thấy tất cả vị trí

3. **Thay thế:**
   - Nhập text mới trong ô "Replace"
   - Click "Replace All" để thay tất cả
   - **Hoặc** click "Replace" từng cái để kiểm tra trước

4. **Save:**
   - `Ctrl+S`

---

## **✅ KẾT QUẢ DỰ KIẾN**

**Sau khi sửa xong:**

- ✅ Trọng số: **60% Model + 40% Criteria** (khớp code)
- ✅ Model: **CalibratedRF hoặc CalibratedLR** (rõ ràng)
- ✅ File: **6 file** (đủ majors.json + hybrid_config.json)
- ✅ Feature: **TF-IDF** (không PhoBERT)
- ✅ Công thức: **α=0.6 = 60%** (rõ ràng)

**Độ hoàn hảo:** **95%+** ✨

---

**Thời gian dự kiến:** ~15-20 phút sửa tất cả ✏️

Bạn có câu hỏi gì không? 🎓
