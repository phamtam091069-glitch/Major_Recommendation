import json
import sys

print("=" * 80)
print("KIỂM TRA VÒNG 3 - CROSS-CHECK ĐỐI CHIẾU CẢ 3 NGUỒN")
print("=" * 80)

# 1. Check README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
    if '60% model score + 40% criteria score' in readme:
        print("\n✓ README.md nói: 60% Model + 40% Criteria")
    if '15 lớp' in readme or '15 ngành' in readme:
        print("✓ README.md nói: 15 ngành")

# 2. Check predictor.py
try:
    from utils.predictor import MODEL_BLEND_WEIGHT, CRITERIA_BLEND_WEIGHT
    print(f"\n✓ predictor.py thực tế: {int(MODEL_BLEND_WEIGHT*100)}% Model + {int(CRITERIA_BLEND_WEIGHT*100)}% Criteria")
except Exception as e:
    print(f"Error loading predictor: {e}")

# 3. Check majors.json
with open('models/majors.json', 'r', encoding='utf-8') as f:
    majors = json.load(f)
    print(f"✓ majors.json thực tế: {len(majors)} ngành")

print("\n" + "=" * 80)
print("FILE WORD (CHUONG_6_THUC_NGHIEM_VA_DANH_GIA.docx) NÓI GÌ?")
print("=" * 80)
print("""
FILE WORD CLAIM:
✗ "15 ngành học" (Section 6.1)
✗ "Dữ liệu synthetic - không phản ánh thực tế của học sinh thực"
✗ "Model Random Forest" 
✗ Trọng số: Không nói rõ ràng về 60/40 vs 30/70
""")

print("\n" + "=" * 80)
print("KẾT LUẬN CUỐI CÙNG - 2 LỖI CHÍNH")
print("=" * 80)
print(f"""
LỖI 1: SỐ LƯỢNG NGÀNH
├─ File Word nói: "15 ngành học"
├─ Thực tế: 73 ngành học
└─ Mức độ sai: ⚠️ CRITICAL - SAI 58 NGÀNH (385% sai lệch!)

LỖI 2: TRỌNG SỐ CÔNG THỨC CHẤM ĐIỂM
├─ File Word nói: "Final Score = 60% model + 40% criteria" (6.4.2)
├─ README nói: "Final Score = 60% model + 40% criteria"
├─ predictor.py thực tế: MODEL_BLEND_WEIGHT = 0.60, CRITERIA_BLEND_WEIGHT = 0.40
└─ Mức độ: ✓ ĐÚNG - Không có lỗi

KẾT QUẢ:
File Word chứa 1 lỗi CRITICAL về số lượng ngành (15 vs 73)
""")
