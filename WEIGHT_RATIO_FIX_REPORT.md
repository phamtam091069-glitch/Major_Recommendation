# 🔧 BÁO CÁO SỬA LỖI: WEIGHT RATIO FIX

## 📋 TÓM TẮT

**Ngày sửa:** 23/04/2026  
**File sửa:** `utils/predictor.py`  
**Lỗi:** Weight ratio đảo ngược (30/70 thay vì 60/40)  
**Trạng thái:** ✅ **FIXED & VERIFIED**

---

## 🔴 VẤN ĐỀ PHÁT HIỆN

### Lỗi #1: Weight Ratio Bị Đảo Ngược (Dòng 33-34)

**Trước fix (SAI):**

```python
CRITERIA_BLEND_WEIGHT = 0.70  # Tiêu chí: 70%
MODEL_BLEND_WEIGHT = 0.30    # Model: 30%
```

**Ảnh hưởng:**

- Final score = 30% Model + 70% Criteria (KHÔNG ĐÚNG)
- Model ML chỉ chiếm 30% → kết quả bị lệch sang tiêu chí
- Không phù hợp với đặc điểm kỹ thuật (README.md nói là 60/40)

---

## ✅ GIẢI PHÁP ÁP DỤNG

### Fix #1: Restore Weight Ratio Đúng (Dòng 33-34)

**Sau fix (ĐÚNG):**

```python
# FIX: Restore correct weight ratio per specification
# Final score = 60% Model + 40% Criteria (per README.md)
MODEL_BLEND_WEIGHT = 0.60    # Model: 60%
CRITERIA_BLEND_WEIGHT = 0.40  # Tiêu chí: 40%
```

**Ảnh hưởng:**

- Final score = 60% Model + 40% Criteria (ĐÚNG)
- Model ML chiếm 60% (vai trò chính) → kết quả chính xác hơn
- Phù hợp với specification (README.md + tài liệu thiết kế)

---

## 📊 CÔNG THỨC TÍNH FINAL SCORE

**Trước fix:**

```
FinalScore = 0.30 × ModelScore + 0.70 × CriteriaScore
             └─ 30% ML ──┘       └─ 70% Criteria ──┘
```

❌ **SAI** - Tiêu chí bị lệch quá cao

**Sau fix:**

```
FinalScore = 0.60 × ModelScore + 0.40 × CriteriaScore
             └─ 60% ML ──┘       └─ 40% Criteria ──┘
```

✅ **ĐÚNG** - Cân bằng giữa ML và Criteria

---

## 🧪 KIỂM THỬ VÀ XÁC NHẬN

### Test 1: Verify Weight Constants

```bash
$ python -c "from utils.predictor import MODEL_BLEND_WEIGHT, CRITERIA_BLEND_WEIGHT; \
  print(f'MODEL_BLEND_WEIGHT: {MODEL_BLEND_WEIGHT} ({int(MODEL_BLEND_WEIGHT*100)}%)'); \
  print(f'CRITERIA_BLEND_WEIGHT: {CRITERIA_BLEND_WEIGHT} ({int(CRITERIA_BLEND_WEIGHT*100)}%)'); \
  print(f'Sum: {MODEL_BLEND_WEIGHT + CRITERIA_BLEND_WEIGHT}')"
```

**Kết quả:** ✅ PASS

```
MODEL_BLEND_WEIGHT: 0.6 (60%)
CRITERIA_BLEND_WEIGHT: 0.4 (40%)
Sum: 1.0
```

---

## 📝 CÁC FILES LIÊN QUAN

### Files Sửa:

- ✅ `utils/predictor.py` - Sửa weight ratio (dòng 33-34)

### Files Backup:

- ✅ `utils/predictor.py.backup` - Backup file cũ

### Files Tham Khảo:

- `README.md` - Specification (Final score = 60% model + 40% criteria)
- `CHUONG_3_QUY_TRINH_DU_LIEU.md` - Tài liệu thiết kế

---

## 🎯 TÁC ĐỘNG DỰ ĐOÁN

### Trước Fix:

- **Problem:** Model chỉ 30% → Dự đoán bị quá tập trung vào tiêu chí
- **Result:** Ngành không phù hợp nhưng có điểm cao nếu match tiêu chí → Sai

### Sau Fix:

- **Solution:** Model 60% (chính) + Criteria 40% (hỗ trợ)
- **Result:** Dự đoán chính xác hơn, cân bằng giữa ML learning + user preference

---

## 📌 HƯỚNG DẪN TIẾP THEO

### 1. **Restart Flask Server**

```bash
# Kill process cũ (nếu đang chạy)
Ctrl+C

# Restart
python app.py
```

### 2. **Test Dự Đoán**

- Vào http://localhost:5000
- Nhập data test
- Verify kết quả dự đoán có hợp lý không

### 3. **Monitor Logs**

Kiểm tra console logs để xem:

- Weight ratio được sử dụng
- Model score & criteria score
- Final score = 60% + 40%

---

## ✅ CHECKLIST HOÀN THÀNH

- [x] Phát hiện lỗi weight ratio
- [x] Xác định nguyên nhân (SAI: 30/70 thay vì 60/40)
- [x] Backup file cũ
- [x] Sửa weight constants (dòng 33-34)
- [x] Verify fix thành công
- [x] Tạo báo cáo chi tiết

---

## 📞 LIÊN HỆ & HỖTRỢ

Nếu gặp vấn đề:

1. Kiểm tra file cũ: `utils/predictor.py.backup`
2. Xem logs flask để debug
3. Chạy test prediction để xác nhận

---

**Status:** ✅ **COMPLETED**  
**Date:** 23/04/2026, 14:52 UTC+7
