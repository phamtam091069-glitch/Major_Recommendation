#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate majors.json với 71 ngành từ dữ liệu students_balanced_400.csv"""

import pandas as pd
import json
import re
from pathlib import Path

# Đường dẫn
data_file = Path(__file__).parent / "data" / "raw" / "students_balanced_400.csv"
output_file = Path(__file__).parent / "models" / "majors.json"

print("=" * 70)
print("GENERATE 71 MAJORS FROM DATA")
print("=" * 70)

# Đọc dữ liệu
print("\n[1] Reading data...")
df = pd.read_csv(data_file)
print(f"    Loaded {len(df)} rows")

# Lấy danh sách ngành (không trùng)
majors_list = df['nganh_phu_hop'].unique()
majors_list = sorted([m for m in majors_list if pd.notna(m)])

print(f"\n[2] Found {len(majors_list)} unique majors")
print(f"    Examples: {majors_list[:5]}")

# Tạo mô tả cho mỗi ngành dựa trên dữ liệu
def create_major_description(major_name, df_major):
    """Tạo mô tả ngành từ dữ liệu"""
    # Lấy các từ khóa từ các trường text
    keywords = set()
    
    # Từ mo_ta_ban_than
    if 'mo_ta_ban_than' in df_major.columns:
        texts = df_major['mo_ta_ban_than'].dropna()
        for text in texts:
            words = str(text).lower().split()
            keywords.update(words[:10])  # Lấy 10 từ đầu
    
    # Từ dinh_huong_tuong_lai
    if 'dinh_huong_tuong_lai' in df_major.columns:
        texts = df_major['dinh_huong_tuong_lai'].dropna()
        for text in texts:
            words = str(text).lower().split()
            keywords.update(words[:10])
    
    # Tạo mô tả
    keywords_text = " ".join(sorted(list(keywords))[:30])
    description = f"{major_name.lower()} {keywords_text}"
    
    return description.strip()

# Generate majors.json mới
majors_json = []

for i, major in enumerate(majors_list, 1):
    # Lấy dữ liệu cho ngành này
    df_major = df[df['nganh_phu_hop'] == major]
    
    # Tạo mô tả
    description = create_major_description(major, df_major)
    
    # Thêm vào list
    majors_json.append({
        "nganh": major,
        "mo_ta": description,
        "samples_count": len(df_major)
    })
    
    if i % 10 == 0:
        print(f"    [{i}/{len(majors_list)}] Processed: {major}")

print(f"\n[3] Created {len(majors_json)} major entries")

# Lưu file JSON
# Loại bỏ samples_count trước khi lưu
majors_json_output = [
    {"nganh": m["nganh"], "mo_ta": m["mo_ta"]}
    for m in majors_json
]

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(majors_json_output, f, ensure_ascii=False, indent=2)

print(f"\n[4] Saved to: {output_file}")
print(f"    File size: {output_file.stat().st_size / 1024:.2f} KB")

# Tóm tắt
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✓ Original majors: 17")
print(f"✓ New majors: {len(majors_json_output)}")
print(f"✓ File: {output_file.name}")
print(f"\nTop 10 majors:")
for i, m in enumerate(majors_json_output[:10], 1):
    print(f"  {i}. {m['nganh']}")

print(f"\n...({len(majors_json_output) - 10} more majors)")
print("\nNext step: Run 'python train_model.py' to retrain with 71 majors!")
print("=" * 70)
