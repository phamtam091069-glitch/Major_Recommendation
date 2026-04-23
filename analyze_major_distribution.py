#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phan tich so luong mau theo tung nganh"""

import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Doc du lieu
df = pd.read_csv('data/raw/students.csv')

print("=" * 80)
print("PHAN TICH PHAN BOA DU LIEU THEO NGANH")
print("=" * 80)

# Tong so nganh
major_counts = df['nganh_phu_hop'].value_counts().sort_values(ascending=False)
print(f"\nTong so nganh khac nhau: {len(major_counts)}")
print(f"Tong so mau: {len(df)}")

print("\n" + "=" * 80)
print("TOP 15 NGANH CO NHIEU MAU NHAT:")
print("=" * 80)
for i, (major, count) in enumerate(major_counts.head(15).items(), 1):
    pct = (count / len(df)) * 100
    print(f"{i:2}. {major:40} | {count:4} mau ({pct:5.1f}%)")

print("\n" + "=" * 80)
print("NGANH CO IT MAU (< 5 mau):")
print("=" * 80)
small_majors = major_counts[major_counts < 5]
print(f"Tong so nganh co < 5 mau: {len(small_majors)}")
for i, (major, count) in enumerate(small_majors.items(), 1):
    print(f"{i:2}. {major:40} | {count:2} mau")

print("\n" + "=" * 80)
print("THONG KE:")
print("=" * 80)
print(f"Trung binh mau/nganh: {len(df) / len(major_counts):.1f}")
print(f"Nganh co tren 20 mau: {len(major_counts[major_counts >= 20])}")
print(f"Nganh co 10-20 mau: {len(major_counts[(major_counts >= 10) & (major_counts < 20)])}")
print(f"Nganh co 5-10 mau: {len(major_counts[(major_counts >= 5) & (major_counts < 10)])}")
print(f"Nganh co < 5 mau: {len(major_counts[major_counts < 5])}")

print("\n" + "=" * 80)
print("TOAN BO NGANH (TAT CA 73 NGANH):")
print("=" * 80)
for i, (major, count) in enumerate(major_counts.items(), 1):
    pct = (count / len(df)) * 100
    print(f"{i:2}. {major:40} | {count:4} mau ({pct:5.1f}%)")

# So sanh voi majors.json
print("\n" + "=" * 80)
print("SO SANH:")
print("=" * 80)
import json
with open('models/majors.json', 'r', encoding='utf-8') as f:
    majors_official = json.load(f)
    majors_list = [m['nganh'] for m in majors_official]
    print(f"Nganh trong majors.json (chinh thuc): {len(majors_list)}")
    print("Danh sach:")
    for i, m in enumerate(majors_list, 1):
        count = major_counts.get(m, 0)
        print(f"  {i:2}. {m:40} | {count:4} mau trong du lieu")

# Nganh trong du lieu nhung khong trong majors.json
majors_in_data_not_in_json = set(major_counts.index) - set(majors_list)
if majors_in_data_not_in_json:
    print(f"\nNganh trong du lieu nhung KHONG co trong majors.json: {len(majors_in_data_not_in_json)}")
    for major in sorted(majors_in_data_not_in_json):
        count = major_counts.get(major, 0)
        print(f"  - {major:40} | {count:4} mau")
