#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

files = {
    'data/raw/students.csv': 'students.csv',
    'data/raw/students_balanced_400.csv': 'students_balanced_400.csv', 
    'data/raw/students_holdout.csv': 'students_holdout.csv',
}

print('CSV FILES ANALYSIS:')
print('=' * 60)

total_rows = 0
for path, name in files.items():
    try:
        df = pd.read_csv(path)
        rows = len(df)
        total_rows += rows
        print(f'{name}: {rows:,} rows')
    except Exception as e:
        print(f'{name}: ERROR - {str(e)}')

print('=' * 60)
print(f'TOTAL ROWS (all CSV files): {total_rows:,}')
