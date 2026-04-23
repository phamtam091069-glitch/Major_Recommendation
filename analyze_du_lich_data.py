"""
Phân tích dữ liệu Du Lịch - Xác định deficit và cần bổ sung
"""
import pandas as pd
import os
import json
from collections import Counter

print("=" * 100)
print("PHÂN TÍCH DỮ LIỆU DU LỊCH VÀ XÁC ĐỊNH NHU CẦU BỔ SUNG")
print("=" * 100)

data_path = "data/raw/students.csv"

if not os.path.exists(data_path):
    print(f"❌ Lỗi: File {data_path} không tồn tại!")
    exit(1)

df = pd.read_csv(data_path)

print(f"\n📊 TỔNG QUÁT DATASET:")
print(f"  • Tổng số mẫu: {len(df)}")
print(f"  • Tổng số ngành: {df['nganh_phu_hop'].nunique()}")
print(f"  • Columns: {', '.join(df.columns.tolist())}")

print(f"\n📈 PHÂN BỐ NGÀNH (Top 15):")
dist = df['nganh_phu_hop'].value_counts()
for i, (major, count) in enumerate(dist.head(15).items(), 1):
    pct = (count / len(df)) * 100
    bar = "█" * int(pct / 2)
    print(f"  {i:2}. {major:45} {count:4} ({pct:5.1f}%) {bar}")

print(f"\n🏖️  DU LỊCH - NGÀNH LIÊN QUAN:")
du_lich_majors = {
    "Du lich": "Du lịch",
    "Quan tri dich vu du lich va lu hanh": "Quản trị dịch vụ du lịch và lữ hành",
}

total_du_lich = 0
du_lich_stats = {}

for major_key, major_display in du_lich_majors.items():
    count = len(df[df['nganh_phu_hop'] == major_key])
    if count > 0:
        pct = (count / len(df)) * 100
        print(f"  • {major_display:45} {count:4} ({pct:5.1f}%)")
        du_lich_stats[major_key] = count
        total_du_lich += count
    else:
        print(f"  • {major_display:45}    0 (0.0%)")
        du_lich_stats[major_key] = 0

pct_total = (total_du_lich / len(df)) * 100
print(f"\n  📊 TỔNG DU LỊCH: {total_du_lich} mẫu ({pct_total:.1f}%)")

print(f"\n📊 PHÂN TÍCH NHU CẦU BỔ SUNG:")
avg_per_major = len(df) / df['nganh_phu_hop'].nunique()
target_per_major = 100  # Mục tiêu mỗi ngành

print(f"  • Trung bình/ngành hiện tại: {avg_per_major:.1f}")
print(f"  • Mục tiêu cân bằng: {target_per_major}/ngành")

total_deficit = 0
deficit_map = {}

for major_key, major_display in du_lich_majors.items():
    count = du_lich_stats.get(major_key, 0)
    deficit = max(0, target_per_major - count)
    deficit_map[major_key] = deficit
    total_deficit += deficit
    
    if deficit > 0:
        print(f"\n  ⚠️  {major_display}")
        print(f"     Hiện tại: {count:3} mẫu")
        print(f"     Cần thêm: {deficit:3} mẫu")
        print(f"     % tăng:  {(deficit/count*100):.0f}%" if count > 0 else f"     % tăng:  ∞ (từ 0)")

print(f"\n💡 KẾ HOẠCH HÀNH ĐỘNG:")
print(f"  • Tổng mẫu cần bổ sung: {total_deficit}")
print(f"  • Tổng mẫu sau bổ sung: {len(df) + total_deficit}")
print(f"  • Sẽ retrain model với dataset cân bằng hơn")

# Lưu deficit info để scripts sau sử dụng
with open("du_lich_deficit.json", "w") as f:
    json.dump({
        "current_total": len(df),
        "target_per_major": target_per_major,
        "deficit": deficit_map,
        "total_deficit": total_deficit,
        "du_lich_stats": du_lich_stats,
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ Phân tích hoàn tất - Lưu vào du_lich_deficit.json")
print("=" * 100)
