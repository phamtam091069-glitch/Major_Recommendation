# 📚 GIẢI THÍCH ĐƠN GIẢN TOÀN BỘ DỰ ÁN

## 🎯 DỰ ÁN LÀ CÁI GÌ?

Hệ thống **AI tư vấn ngành học** dùng Flask:

- Người dùng nhập: Sở thích, kỹ năng, tính cách...
- Hệ thống trả lời: **Top 3 ngành phù hợp nhất** + điểm số

---

## 🏗️ CẤU TRÚC HỆ THỐNG

### Backend (Máy chủ) - `app.py` + `utils/`

- Nhận dữ liệu từ form
- Dùng **Machine Learning** để dự đoán
- Trả lại kết quả JSON

### Frontend (Giao diện) - `templates/` + `static/`

- Form nhập thông tin người dùng
- Chatbot tương tác
- Hiển thị kết quả

### Dữ liệu - `data/` + `models/`

- **Dữ liệu học sinh**: `data/raw/students.csv` (10,650 học sinh)
- **Mô hình AI**: `models/rf_model.pkl` (được train từ dữ liệu)
- **Cấu hình ngành**: `models/majors.json` (73 ngành)

---

## 🧠 CÁCH TÍNH ĐIỂM (QUAN TRỌNG!)

```
ĐIỂM CUỐI = 30% x Điểm từ ML + 70% x Điểm tiêu chí

Trong đó:
- Điểm ML: Từ mô hình Random Forest (máy học)
- Điểm tiêu chí: Từ 8 tiêu chí cố định:
  - Sở thích: 23%
  - Định hướng: 20%
  - Kỹ năng: 16%
  - Tính cách: 14%
  - Môi trường: 12%
  - Môn học: 8%
  - Mô tả: 4%
  - Mục tiêu: 3%
```

---

## 📊 CÓ 73 NGÀNH TRONG HỆ THỐNG

### Các ngành chính:

1. **Công nghệ** (15 ngành): CNTT, Kỹ thuật, Data Science, AI...
2. **Kinh doanh** (10 ngành): Marketing, Kế toán, Quản lý...
3. **Y tế** (12 ngành): Bác sĩ, Dược, Điều dưỡng...
4. **Giáo dục** (8 ngành): Sư phạm Toán, Tin, Sinh...
5. **Sáng tạo** (12 ngành): Thiết kế, Kiến trúc, Nhiếp ảnh...
6. **Hàng hải** (2 ngành): **← BẠN HỎI VỀ NGÀNH NÀY**
7. Và nhiều ngành khác...

---

## 🚢 VẤN ĐỀ: 2 NGÀNH HÀNG HẢI KHÔNG HIỂN THỊ

### 2 ngành hàng hải là gì?

1. **Điều khiển và quản lý tàu biển** 🚢
   - Mục đích: Dạy cách điều khiển tàu biển
   - Công việc: Thuyền trưởng, sĩ quan hàng hải

2. **Khai thác máy tàu thủy và quản lý kỹ thuật** ⚙️
   - Mục đích: Dạy quản lý máy tàu
   - Công việc: Sĩ quan máy, kỹ sư hàng hải

### Tình trạng hiện tại:

✅ **CÓ trong hệ thống:**

- Tên ngành trong `models/majors.json` ✓
- Tên tiếng Việt trong `MAJOR_DISPLAY` ✓
- Yêu cầu tính cách trong `MAJOR_PERSONALITY_REQUIREMENTS` ✓
- Gợi ý trong `SUGGESTION_VI` ✓
- Dữ liệu huấn luyện: **150 học sinh mỗi ngành** ✓

❌ **NHƯNG KHÔNG HIỂN THỊ** vì sao?

---

## 🔴 NGUYÊN NHÂN CHÍNH

### Vấn đề:

**Mô hình ML (`models/rf_model.pkl`) chưa được train lại!**

### Giải thích:

```
Timeline:
- Ngày cũ: Hệ thống có 71 ngành
- → Train mô hình → Mô hình biết 71 ngành
- Ngày mới: Thêm 2 ngành hàng hải → Bây giờ có 73 ngành
- → MỘ HÌNH VẪN BIẾT 71 NGÀNH CŨ ❌
- → Nên 2 ngành mới không được dự đoán được
```

### Ví dụ dễ hiểu:

- Bạn train bé thứ 1 nhận dạng: **chó, mèo, chim** (3 loài)
- Sau đó bạn thêm: **cá, rùa** (5 loài)
- Bé thứ 1 vẫn chỉ biết 3 loài cũ → Không nhận dạng được cá & rùa
- Cần **train lại bé** để nó học 5 loài mới

---

## ✅ GIẢI PHÁP

### Bước 1: Chạy lệnh này

```bash
python train_model.py
```

### Bước 2: Chờ train hoàn thành (5-10 phút)

- Mô hình sẽ:
  - Đọc dữ liệu 10,650 học sinh (bao gồm 2 ngành hàng hải)
  - Learn pattern mới
  - Save vào `models/rf_model.pkl`

### Bước 3: Restart Flask

```bash
python app.py
```

### Bước 4: Test

- Truy cập form
- Chọn sở thích liên quan đến hàng hải
- Xem kết quả có 2 ngành hàng hải không

---

## 📊 KẾT QUẢ KIỂM TRA

### Tómo tắt:

- ✅ **68 ngành**: Hoàn thiện 100% (có tất cả thông tin)
- ⚠️ **5 ngành**: Thiếu thông tin nhỏ (personality hoặc suggestion)
- 🚢 **2 ngành hàng hải**: Có dữ liệu nhưng cần train lại

### 5 ngành chưa hoàn thiện:

1. Địa lý học - Thiếu: Tính cách + Gợi ý
2. Khoa học môi trường - Thiếu: Gợi ý
3. Công nghệ thực phẩm - Thiếu: Gợi ý
4. Sư phạm Giáo dục thể chất - Thiếu: Tính cách + Gợi ý
5. Quản lý thể thao - Thiếu: Tính cách + Gợi ý

---

## 🔧 CÁC SCRIPT KIỂM TRA ĐƯỢC TẠO

### 1. `check_major_classification.py`

**Dùng để:** Kiểm tra tất cả 73 ngành
**Chạy:** `python check_major_classification.py`
**Output:** Chi tiết từng ngành thiếu gì

### 2. `check_marine_majors.py`

**Dùng để:** Kiểm tra 2 ngành hàng hải cụ thể
**Chạy:** `python check_marine_majors.py`
**Output:** Danh sách tất cả ngành + vị trí 2 ngành hàng hải

### 3. `MAJOR_CLASSIFICATION_REPORT.md`

**Dùng để:** Báo cáo chi tiết toàn bộ
**Nội dung:** 70 trang chi tiết

---

## 🎓 HÀNH ĐỘNG TIẾP THEO

### Ưu tiên 1 (NGAY): Giúp 2 ngành hàng hải hiển thị

```bash
python train_model.py
python app.py
# Test trên web
```

### Ưu tiên 2 (SAU): Hoàn thiện 5 ngành còn lại

- Mở `utils/constants.py`
- Thêm thông tin cho 5 ngành thiếu
- Train lại mô hình

### Ưu tiên 3 (KIỂM TRA): Xác thực lại

```bash
python check_major_classification.py
```

---

## 🎯 TÓMO TẮT 1 CÂUTEXT

**Tất cả 73 ngành đã cấu hình đầy đủ, 2 ngành hàng hải có dữ liệu nhưng cần `python train_model.py` để mô hình học dữ liệu mới.**
