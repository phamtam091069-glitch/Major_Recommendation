# ⚠️ BÁO CÁO XUNG ĐỘT FILE MODEL

**Ngày:** 23/04/2026 13:32  
**Status:** 🔴 PHÁT HIỆN CÓ XUNG ĐỘT

---

## 📊 TÓM TẮT

| Vấn Đề                      | Mức Độ      | Trạng Thái |
| --------------------------- | ----------- | ---------- |
| majors.json cũ (26.5 giờ)   | ⚠️ Cảnh báo | Cần sửa    |
| tfidf.pkl bị lỗi            | ❌ Lỗi      | Cần sửa    |
| classes.pkl vs rf_model.pkl | ❌ Mismatch | Cần sửa    |

---

## 🔍 CHI TIẾT TỪNG XUNG ĐỘT

### 1️⃣ XUNG ĐỘT: majors.json CŨ

**Vấn Đề:**

```
File cũ nhất: majors.json (2026-04-22 11:00:43)
File mới nhất: hybrid_config.json (2026-04-23 13:29:00)
Chênh lệch: 26.5 giờ
```

**Nguyên Nhân:**

- majors.json không được cập nhật khi train model mới
- Model mới được train với 73 ngành (phiên bản mới - 400 mẫu/ngành)
- Nhưng majors.json cũ vẫn được giữ lại

**Hậu Quả:**

- Model có 73 ngành nhưng majors.json chỉ có 73 ngành (may mắn!)
- Nhưng format có thể khác nhau (cũ vs mới)

**Giải Pháp:**

```bash
# Cập nhật majors.json từ phiên bản mới
# Chạy train_model.py sẽ tự động cập nhật majors.json
python train_model.py
```

---

### 2️⃣ XUNG ĐỘT: tfidf.pkl Bị Lỗi

**Vấn Đề:**

```
❌ tfidf.pkl | Lỗi: invalid load key, '\x10'
```

**Nguyên Nhân:**

- File pickle bị hỏng hoặc corrupt
- Có thể do lỗi trong quá trình save hoặc network interrupt

**Hậu Quả:**

- Không thể load tfidf.pkl
- Prediction sẽ fail khi cần TF-IDF features

**Giải Pháp:**

```bash
# Xóa file hỏng và train lại
rm models/tfidf.pkl
python train_model.py
```

---

### 3️⃣ XUNG ĐỘT: classes.pkl vs rf_model.pkl

**Vấn Đề:**

```
rf_model.pkl: Type = ndarray (không đọc được n_classes_)
classes.pkl: Type = list | Classes = 71
```

**Nguyên Nhân:**

- rf_model.pkl là ndarray (không phải sklearn model object)
- classes.pkl chỉ có 71 classes
- Nhưng majors.json có 73 classes

**Hậu Quả:**

- Mismatch giữa số classes
- Prediction có thể miss 2 ngành

**Giải Pháp:**

```bash
# Train lại model để fix
python train_model.py
```

---

## 🚨 XUNG ĐỘT CHI TIẾT

### Problem 1: majors.json Format

**Vấn Đề Chi Tiết:**

- majors.json được load thành list, không phải dict
- Script cố gắng gọi `.keys()` trên list → Lỗi

**Code problematic:**

```python
majors = json.load(f)  # Returns list, not dict
n_majors = len(majors)  # OK
majors.keys()  # ❌ ERROR: list không có .keys()
```

**Cách Fix:**

```python
majors = json.load(f)  # majors là list
if isinstance(majors, list):
    major_names = [m.get('nganh') for m in majors]
    n_majors = len(majors)
else:  # majors là dict
    major_names = list(majors.keys())
    n_majors = len(majors)
```

---

### Problem 2: tfidf.pkl Corrupt

**Vấn Đề Chi Tiết:**

- File pickle invalid (invalid load key)
- Dung lượng: 40,477 bytes (hợp lý)
- Nhưng không thể deserialize

**Khả năng Nguyên Nhân:**

1. Lỗi khi save (timeout, disk full, crash)
2. File bị overwrite không đúng
3. Python version mismatch (unlikely)

**Cách Fix:**

```bash
# Xóa file bị lỗi
rm c:\Users\huyen\Downloads\major-recommendation\models\tfidf.pkl

# Train lại
python train_model.py
```

---

### Problem 3: Số Classes Không Match

**Vấn Đề Chi Tiết:**

```
classes.pkl: 71 classes
majors.json: 73 ngành
rf_model.pkl: ndarray (không thể đọc)
```

**Nguyên Nhân Có Thể:**

- Dữ liệu training có 71 ngành
- Nhưng majors.json thêm 2 ngành mới

**Hậu Quả:**

- 2 ngành trong majors.json không có trong training data
- Prediction sẽ không thể predict những ngành này

**Cách Fix:**

```bash
# Train lại với dữ liệu mới
# Đảm bảo 73 ngành được train
python train_model.py
```

---

## ✅ GIẢI PHÁP KHUYẾN NGHỊ

### Bước 1: Xóa File Bị Lỗi

```bash
# Xóa các file potentially corrupted
rm models/tfidf.pkl
rm models/rf_model.pkl
rm models/ohe.pkl
rm models/classes.pkl
rm models/majors.json
rm models/hybrid_config.json
```

### Bước 2: Train Lại Model

```bash
# Train sẽ tạo lại tất cả file
python train_model.py
```

### Bước 3: Kiểm Tra Lại

```bash
# Chạy script kiểm tra xung đột
python check_model_conflicts.py
```

---

## 📈 EXPECTED RESULT SAU KHI FIX

```
✅ KHÔNG CÓ XUNG ĐỘT - Tất cả file model đều hợp lệ và khớp nhau

Timestamp:
- Tất cả file cùng ngày/giờ
- Chênh lệch < 1 giờ ✅

Config:
- model: CalibratedLogisticRegression ✅
- tfidf_max_features: 1200 ✅

Pickle Files:
- rf_model.pkl: CalibratedClassifierCV ✅
- classes.pkl: 73 classes ✅
- ohe.pkl: OneHotEncoder ✅
- tfidf.pkl: TfidfVectorizer ✅

Majors:
- Tổng số: 73 ngành ✅
- Format: List of dict ✅
```

---

## 🎯 QUICK FIX (5 PHÚT)

```bash
# 1. Xóa file cũ
del models\tfidf.pkl
del models\rf_model.pkl
del models\ohe.pkl
del models\classes.pkl

# 2. Train lại (10-15 phút, nhưng xử lý offline)
python train_model.py

# 3. Kiểm tra
python check_model_conflicts.py

# 4. Khởi động lại app (load model mới)
python app.py
```

---

## 📋 CHECKLIST

- [ ] Xóa file bị lỗi (tfidf.pkl, rf_model.pkl)
- [ ] Chạy train_model.py
- [ ] Chạy check_model_conflicts.py để verify
- [ ] Khởi động lại app.py
- [ ] Test predict API
- [ ] Confirm không còn xung đột

---

## 📞 CẦN HỖ TRỢ?

Nếu sau khi train lại vẫn có lỗi:

1. **Kiểm tra dữ liệu training:**

   ```bash
   python -c "import pandas as pd; df=pd.read_csv('data/raw/students_balanced_400.csv'); print(f'Rows: {len(df)}, Majors: {df[\"major\"].nunique()}')"
   ```

2. **Kiểm tra train_model.py log:**

   ```bash
   python train_model.py 2>&1 | tee train_debug.log
   ```

3. **Xóa toàn bộ models directory và train từ đầu:**
   ```bash
   rm -r models/*
   python train_model.py
   ```

---

**Generated:** 2026-04-23 13:32  
**Status:** ⚠️ CẦN KHẮC PHỤC  
**Priority:** 🔴 CAO - Ảnh hưởng đến prediction
