#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPREHENSIVE VERIFICATION - Kiem tra tat ca cac loi trong file Word
Vai tro: Thay giao kho tinh - Xac minh 100% chinh xac
"""

import json
import sys
from pathlib import Path

def get_majors_count():
    """Loi 1: So luong nganh"""
    with open('models/majors.json', 'r', encoding='utf-8') as f:
        majors = json.load(f)
    return len(majors)

def get_data_generator_info():
    """Loi 2: So luong mau va phan bo"""
    with open('data/generate_balanced_students.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract ROWS_PER_MAJOR
    for line in content.split('\n'):
        if 'ROWS_PER_MAJOR =' in line:
            rows_per_major = int(line.split('=')[1].strip())
        if 'MAJORS_ORDER = [' in line:
            # Count majors in the list
            start_idx = content.find('MAJORS_ORDER = [')
            end_idx = content.find(']', start_idx)
            majors_section = content[start_idx:end_idx]
            majors_in_list = majors_section.count('"')
            majors_count_in_code = majors_in_list // 2
    
    return rows_per_major, majors_count_in_code

def get_model_config():
    """Loi 3: Model type va config"""
    with open('models/hybrid_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_predictor_weights():
    """Loi 4: Trong so trong predictor.py"""
    with open('utils/predictor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    model_weight = None
    criteria_weight = None
    for line in content.split('\n'):
        if 'MODEL_BLEND_WEIGHT = ' in line:
            model_weight = float(line.split('=')[1].strip())
        if 'CRITERIA_BLEND_WEIGHT = ' in line:
            criteria_weight = float(line.split('=')[1].strip())
    
    return model_weight, criteria_weight

def get_evaluation_metrics():
    """Loi 5: Ket qua evaluation"""
    eval_file = Path('reports/evaluation.txt')
    if not eval_file.exists():
        return None
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def main():
    print("=" * 90)
    print("KIEM TRA TOAN DIEN - CHI TIET TAT CA CAC LOI")
    print("=" * 90)
    
    errors_found = []
    
    # ERROR 1: So luong nganh
    print("\n[VONG 1] Kiem tra so luong nganh")
    print("-" * 90)
    majors_count = get_majors_count()
    print(f"Thuc te: {majors_count} nganh")
    print(f"File Word noi: 15 nganh")
    if majors_count != 15:
        errors_found.append(f"LOI 1 (CRITICAL): So nganh sai - {majors_count} vs 15")
        print(f">>> LOI PHAT HIEN: SAI {majors_count - 15} nganh")
    
    # ERROR 2: So mau va phan bo
    print("\n[VONG 2] Kiem tra so luong mau va phan bo")
    print("-" * 90)
    rows_per_major, majors_in_code = get_data_generator_info()
    total_rows_expected = rows_per_major * majors_in_code
    print(f"Rows per major: {rows_per_major}")
    print(f"Majors in MAJORS_ORDER: {majors_in_code}")
    print(f"Tong so mau (trong code): {total_rows_expected}")
    print(f"File Word noi: 1200 mau cho 15 nganh")
    
    if majors_in_code != 15:
        errors_found.append(f"LOI 2: So nganh trong MAJORS_ORDER sai - {majors_in_code} vs 15")
        print(f">>> LOI PHAT HIEN: MAJORS_ORDER co {majors_in_code} nganh, khong phai 15")
    
    if total_rows_expected != 1200:
        errors_found.append(f"LOI 2b: Tong so mau sai - {total_rows_expected} vs 1200")
        print(f">>> LOI PHAT HIEN: Tong mau = {total_rows_expected} (khong phai 1200)")
    
    # ERROR 3: Model type
    print("\n[VONG 3] Kiem tra model type va config")
    print("-" * 90)
    model_config = get_model_config()
    print(f"Model trong hybrid_config.json: {model_config.get('model')}")
    print(f"File Word noi: Random Forest hoac CalibratedLogisticRegression")
    model_type = model_config.get('model', '')
    if 'CalibratedLogisticRegression' in model_type:
        print(">>> OK: Model la CalibratedLogisticRegression (hop le)")
    elif 'RandomForest' in model_type:
        print(">>> OK: Model la RandomForest (hop le)")
    else:
        errors_found.append(f"LOI 3: Model type khong ro - {model_type}")
    
    # ERROR 4: Hybrid weights
    print("\n[VONG 4] Kiem tra trong so hybrid weights")
    print("-" * 90)
    model_weight, criteria_weight = get_predictor_weights()
    print(f"predictor.py - MODEL_BLEND_WEIGHT: {model_weight}")
    print(f"predictor.py - CRITERIA_BLEND_WEIGHT: {criteria_weight}")
    print(f"File Word noi: Final Score = 60% model + 40% criteria")
    
    if model_weight == 0.60 and criteria_weight == 0.40:
        print(">>> OK: Trong so chinh xac (60/40)")
    else:
        errors_found.append(f"LOI 4: Trong so sai - {model_weight}/{criteria_weight} vs 0.60/0.40")
    
    # ERROR 5: Ket qua evaluation
    print("\n[VONG 5] Kiem tra ket qua evaluation")
    print("-" * 90)
    eval_content = get_evaluation_metrics()
    if eval_content:
        # Extract first few lines
        lines = eval_content.split('\n')[:20]
        for line in lines:
            if line.strip():
                print(f"  {line}")
    else:
        print(">>> CANH BAO: Khong co file reports/evaluation.txt")
    
    # SUMMARY
    print("\n" + "=" * 90)
    print("TONG KET - TAT CA CAC LOI")
    print("=" * 90)
    
    if errors_found:
        print(f"\nTong cong phat hien: {len(errors_found)} loi\n")
        for i, error in enumerate(errors_found, 1):
            print(f"{i}. {error}")
    else:
        print("\nKhong phat hien loi nao!")
    
    print("\n" + "=" * 90)

if __name__ == '__main__':
    main()
