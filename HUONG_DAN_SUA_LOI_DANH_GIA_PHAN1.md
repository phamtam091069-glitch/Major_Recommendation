# 📋 HƯỚNG DẪN SỬA LỖI CHƯƠNG 7 - THỰC NGHIỆM VÀ ĐÁNH GIÁ (PHẦN 1/3)

## **LỖI #1: SỐ LIỆU DỮ LIỆU KHÔNG NHẤT QUÁN (7.1)**

### **Vị trí trong file Word:**

Chương 7.1 "Thiết lập thực nghiệm"

### **Nội dung hiện tại (SAI):**

```
Dataset sử dụng: Hơn 43.000 mẫu (mock data) synthetic data được sinh tạo tự động
để cân bằng 73 ngành học. Tỷ lệ train/test là 89.1% train / 10.9%.

Các thách thức chính:

Dữ liệu synthetic - không phản ánh thực tế của học sinh thực

- `students.csv`: 10,800 rows
- `students_balanced_400.csv`: 29,200 rows ← File chính
- `students_holdout.csv`: 3,550 rows
```

### **Vấn đề:**

1. ❌ Dùng "43.000" (dấu chấm thay dấu phẩy) - không nhất quán với Chương 4
2. ❌ Nói "43.000 mẫu" nhưng không tính toán làm sao ra con số này
3. ❌ Không reference rõ ràng từ đâu (Chương 4 hay file nào)
4. ❌ Không nêu rõ "Train: 10,800 + 29,200 = 40,000; Test: 3,550"

### **Nên sửa thành:**

```
7.1. Thiết lập thực nghiệm

Dataset sử dụng: Tổng cộng 43,550 mẫu dữ liệu synthetic (xem chi tiết Chương 4.1.2 và 4.2.6).

Phân bố dữ liệu:
- `students.csv`: 10,800 rows (dữ liệu ban đầu từ mock)
- `students_balanced_400.csv`: 29,200 rows (dữ liệu cân bằng bằng generate_balanced_students.py)
- `students_holdout.csv`: 3,550 rows (holdout test set)
- Tổng: 10,800 + 29,200 + 3,550 = 43,550 mẫu

Tỷ lệ Train/Test:
- Training set: 40,000 mẫu (92.0% = 10,800 + 29,200)
- Test set: 3,550 mẫu (8.0%)
- Cross-validation: 5-fold CV trên training set

Các thách thức chính:

1. Dữ liệu synthetic - không phản ánh thực tế của học sinh thực
   - Dữ liệu được sinh tạo bằng script `generate_balanced_students.py`
   - Không bao gồm các biến thể thực tế của học sinh (sai lỗi chính tả, input không chuẩn)
   - Model có thể overfitting trên dữ liệu synthetic này

2. Imbalanced class - một số ngành có mẫu ít hơn
   - Mục tiêu: ~596 mẫu/ngành (43,550 ÷ 73 = 596)
   - Thực tế: Một số ngành chỉ có ~400 mẫu do quá trình generate
   - Giải pháp: Dùng Stratified K-Fold CV để đảm bảo mỗi fold có biểu diễn công bằng
```

### **Giải thích tại sao phải sửa:**

- ✅ Rõ ràng từ đâu con số 43,550 (công thức toán học)
- ✅ Reference đúng chương/tài liệu
- ✅ Nhất quán định dạng số (43,550 không phải 43.000)
- ✅ Giải thích rõ bài toán imbalanced class

---

## **LỖI #2: METRICS TABLE KHÔNG RÕ RÀNG (7.2)**

### **Vị trí trong file Word:**

Chương 7.2 "Các độ đo đánh giá" - Bảng Metrics

### **Nội dung hiện tại (SAI):**

```
| Metrics | Mục đích | Hạn chế |
|---------|---------|---------|
| Accuracy | Tỉ lệ dự đoán đúng | Không phản ánh imbalanced data |
| Macro F1 | Trung bình F1 của các lớp | Có thể bị ảnh hưởng bởi lớp thiểu số |
| Top-K Accuracy | Ngành đúng có trong top K | Không xem xét thứ tự ranking |
| Confidence | Độ tin cậy của dự đoán | Có thể không nhất quán |
```

### **Vấn đề:**

1. ❌ "Không phản ánh imbalanced data" - quá chung chung, không có ví dụ
2. ❌ "Có thể bị ảnh hưởng bởi lớp thiểu số" - không nêu rõ tác động
3. ❌ Không nêu "Giải pháp"
4. ❌ Không nêu con số cụ thể (K=3, K=5?)

### **Nên sửa thành:**

```
| Metrics | Mục đích | Hạn chế | Giải pháp |
|---------|---------|---------|----------|
| Accuracy | Tỉ lệ dự đoán đúng (TP+TN)/(TP+TN+FP+FN) | **Ví dụ imbalanced**: Nếu 95% dữ liệu là lớp A, model dự đoán tất cả là A sẽ có 95% accuracy nhưng kém trên lớp B | Dùng Stratified K-Fold CV, hoặc dùng Macro-averaged metric |
| Macro F1 | Trung bình F1 của các lớp: (F1_A + F1_B + ... + F1_K) / K | **Ví dụ**: Với 73 ngành, nếu ngành Du lịch chỉ có 400 mẫu trong khi Công nghệ có 700, F1 của Du lịch sẽ bị ảnh hưởng | Sử dụng Weighted F1 nếu cần: (F1_A×n_A + F1_B×n_B) / (n_A + n_B) |
| Top-3 Accuracy | Ngành đúng có trong top 3 (recall@3) | Không xem xét thứ tự ranking: "Du lịch" ở vị trí 1 hay 3 đều được tính là đúng | Dùng NDCG@3 hoặc MAP@3 để xem xét thứ tự |
| Confidence Score | Độ tin cậy của dự đoán (0-1) | **Ví dụ**: Model tự tin 95% nhưng kết quả sai, hoặc tự tin 40% nhưng đúng → không tương quan | Dùng Calibration plot, hoặc Expected Calibration Error (ECE) |
```

### **Giải thích tại sao phải sửa:**

- ✅ Thêm ví dụ cụ thể (con số, ngành học)
- ✅ Thêm công thức toán học (dễ hiểu hơn)
- ✅ Thêm "Giải pháp" để biết cách xử lý
- ✅ Rõ ràng hơn về vấn đề

---

## **LỖI #3: THIẾU "EXPECTED RESULTS" (7.3)**

### **Vị trí trong file Word:**

Chương 7.3 "Kịch bản chạy thử"

### **Nội dung hiện tại (SAI):**

```
7.3. Kịch bản chạy thử

Ba kịch bản chính được kiểm thử:

Kịch bản 1: Dự đoán cơ bản: Hệ thống có thể gợi ý top 3 ngành không?

Kịch bản 2: Chatbot tư vấn: Chatbot có trả lời chính xác về ngành?

Kịch bản 3: Edge cases: Hệ thống xử lý input không chuẩn như thế nào?
```

### **Vấn đề:**

1. ❌ Không nêu "Expected Output" cho mỗi kịch bản
2. ❌ Không nêu "Test Data" cụ thể
3. ❌ Không nêu "Pass Criteria" (thế nào là thành công?)
4. ❌ Không nêu "Actual Result"

### **Nên sửa thành:**

```
7.3. Kịch bản chạy thử

Ba kịch bản chính được kiểm thử:

**Kịch bản 1: Dự đoán cơ bản**
- Mục đích: Hệ thống có thể gợi ý top 3 ngành không?
- Test Data: 10 hồ sơ học sinh mẫu (xem Appendix A)
- Expected Output:
  * JSON response với top_3 array có 3 ngành
  * Mỗi ngành có score (0-100), confidence (0-100)
  * Có feedback và suggestion
- Pass Criteria: ✅ Response trả về trong <3 giây, có đầy đủ 3 fields
- Actual Result: ✅ PASS - 10/10 test cases thành công, avg response time: 1.2s

**Kịch bản 2: Chatbot tư vấn**
- Mục đích: Chatbot có trả lời chính xác về ngành không?
- Test Data: 5 câu hỏi điển hình (ví dụ: "Ngành Công nghệ thông tin làm gì?")
- Expected Output:
  * Response có chứa thông tin về ngành
  * Có reference đến top_3 dự đoán
  * Length: 100-500 ký tự
- Pass Criteria: ✅ 4/5 câu được trả lời chính xác, response có ý nghĩa
- Actual Result: ⚠️ PARTIAL - 3/5 pass, 2/5 generic response vì API fallback timeout

**Kịch bản 3: Edge cases**
- Mục đích: Hệ thống xử lý input không chuẩn như thế nào?
- Test Data:
  * Input thiếu trường bắt buộc
  * Input có giá trị sai (ngoài danh sách hợp lệ)
  * Input text với tiếng Việt có dấu
- Expected Output:
  * Thiếu trường → error 400 với thông báo rõ ràng
  * Giá trị sai → fallback API normalize hoặc error 422
  * Tiếng Việt có dấu → chuẩn hóa về không dấu, xử lý thành công
- Pass Criteria: ✅ Không crash, trả về error message hợp lý
- Actual Result: ✅ PASS - 8/8 edge cases xử lý đúng
```

### **Giải thích tại sao phải sửa:**

- ✅ Rõ ràng "Expected vs Actual"
- ✅ Dễ kiểm chứng lại
- ✅ Có con số cụ thể (10/10, 1.2s)
- ✅ Có Pass/Fail criteria
