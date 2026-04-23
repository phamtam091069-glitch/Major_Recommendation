#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm tra kích thước các file CSV"""

import pandas as pd
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

data_raw_path = os.path.join(os.path.dirname(__file__), 'data', 'raw')

files_to_check = [
    'students.csv',
    'students_balanced_400.csv',
    'students_holdout.csv',
    'students_1200.csv',
    'students_balanced_29000.csv',
    'students_29000.csv'
]

print("=" * 70)
print("KIEM TRA KICH THUOC FILE CSV")
print("=" * 70)

for f in files_to_check:
    full_path = os.path.join(data_raw_path, f)
    if os.path.exists(full_path):
        try:
            df = pd.read_csv(full_path)
            file_size_mb = os.path.getsize(full_path) / (1024 * 1024)
            print(f"{f:40} | {len(df):6} rows | {file_size_mb:8.2f} MB")
        except Exception as e:
            print(f"{f:40} | ERROR: {str(e)[:30]}")
    else:
        print(f"{f:40} | NOT FOUND")

# Also check for any other CSV files in data/raw
print("\n" + "=" * 70)
print("CONG TIM CAC FILE CSV KHAC TRONG data/raw:")
print("=" * 70)

if os.path.exists(data_raw_path):
    all_csv_files = [f for f in os.listdir(data_raw_path) if f.endswith('.csv')]
    for f in all_csv_files:
        if f not in files_to_check:
            full_path = os.path.join(data_raw_path, f)
            try:
                df = pd.read_csv(full_path)
                file_size_mb = os.path.getsize(full_path) / (1024 * 1024)
                print(f"{f:40} | {len(df):6} rows | {file_size_mb:8.2f} MB")
            except Exception as e:
                print(f"{f:40} | ERROR: {str(e)[:30]}")
