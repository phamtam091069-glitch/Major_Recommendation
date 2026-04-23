#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra xung đột giữa các file model
"""
import json
import pickle
import os
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("KIỂM TRA XUNG ĐỘT FILE MODEL")
print("="*80)
print()

models_dir = Path("models")

# 1. Kiểm tra file tồn tại
print("1️⃣  KIỂM TRA FILE CÓ TỒN TẠI KHÔNG")
print("-" * 80)

required_files = [
    "rf_model.pkl",
    "ohe.pkl",
    "tfidf.pkl",
    "classes.pkl",
    "hybrid_config.json",
    "majors.json"
]

file_status = {}
for f in required_files:
    path = models_dir / f
    exists = path.exists()
    file_status[f] = exists
    status = "✅ CÓ" if exists else "❌ THIẾU"
    if exists:
        size = path.stat().st_size
        mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{status} | {f:25s} | {size:10,d} bytes | {mtime}")
    else:
        print(f"{status} | {f:25s}")

all_exist = all(file_status.values())
if all_exist:
    print("\n✅ Tất cả file đều tồn tại\n")
else:
    print("\n❌ CẢNH BÁO: Một số file bị thiếu!\n")

print()

# 2. Kiểm tra timestamp (ngày tháng) để phát hiện bản cũ/mới
print("2️⃣  KIỂM TRA PHIÊN BẢN (Timestamp)")
print("-" * 80)

timestamps = {}
for f in required_files:
    path = models_dir / f
    if path.exists():
        mtime = path.stat().st_mtime
        timestamps[f] = mtime

if timestamps:
    sorted_files = sorted(timestamps.items(), key=lambda x: x[1])
    oldest = sorted_files[0]
    newest = sorted_files[-1]
    
    print(f"File cũ nhất: {oldest[0]}")
    print(f"File mới nhất: {newest[0]}")
    print()
    
    # Kiểm tra xem có file cũ không
    time_diff = newest[1] - oldest[1]
    if time_diff > 3600:  # Hơn 1 giờ
        print("⚠️  CẢNH BÁO: Có sự chênh lệch thời gian lớn giữa các file!")
        print(f"   Chênh lệch: {time_diff / 3600:.1f} giờ")
        print(f"   → Có thể có file cũ/mới không khớp nhau")
    else:
        print("✅ Tất cả file được tạo gần như cùng lúc (OK)")

print()
print()

# 3. Kiểm tra config
print("3️⃣  KIỂM TRA CONFIG (hybrid_config.json)")
print("-" * 80)

config_path = models_dir / "hybrid_config.json"
if config_path.exists():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ Config hợp lệ:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        # Kiểm tra các tham số quan trọng
        if config.get("model") != "CalibratedLogisticRegression":
            print(f"\n⚠️  CẢNH BÁO: Model là '{config.get('model')}' (có thể không phải phiên bản mới nhất)")
        
        if config.get("tfidf_max_features") != 1200:
            print(f"\n⚠️  CẢNH BÁO: TF-IDF max_features = {config.get('tfidf_max_features')} (mong đợi 1200)")
    
    except Exception as e:
        print(f"❌ Lỗi đọc config: {e}")

print()
print()

# 4. Kiểm tra consistency của pickle files
print("4️⃣  KIỂM TRA CONSISTENCY (Pickle Files)")
print("-" * 80)

pickle_files = ["rf_model.pkl", "ohe.pkl", "tfidf.pkl", "classes.pkl"]
pickle_info = {}

for f in pickle_files:
    path = models_dir / f
    if path.exists():
        try:
            with open(path, 'rb') as pkl_file:
                obj = pickle.load(pkl_file)
            
            obj_type = type(obj).__name__
            
            if f == "rf_model.pkl":
                # Kiểm tra model
                if hasattr(obj, 'n_classes_'):
                    n_classes = obj.n_classes_
                    print(f"✅ {f:20s} | Type: {obj_type:30s} | Classes: {n_classes}")
                    pickle_info[f] = n_classes
                else:
                    print(f"✅ {f:20s} | Type: {obj_type}")
            
            elif f == "ohe.pkl":
                # One-Hot Encoder
                if hasattr(obj, 'n_features_in_'):
                    n_features = obj.n_features_in_
                    print(f"✅ {f:20s} | Type: {obj_type:30s} | Features: {n_features}")
                else:
                    print(f"✅ {f:20s} | Type: {obj_type}")
            
            elif f == "tfidf.pkl":
                # TF-IDF Vectorizer
                if hasattr(obj, 'max_features'):
                    max_feat = obj.max_features
                    print(f"✅ {f:20s} | Type: {obj_type:30s} | Max Features: {max_feat}")
                else:
                    print(f"✅ {f:20s} | Type: {obj_type}")
            
            elif f == "classes.pkl":
                # Classes
                if isinstance(obj, list):
                    n_classes = len(obj)
                    print(f"✅ {f:20s} | Type: {obj_type:30s} | Classes: {n_classes}")
                    pickle_info[f] = n_classes
                else:
                    print(f"✅ {f:20s} | Type: {obj_type}")
        
        except Exception as e:
            print(f"❌ {f:20s} | Lỗi: {e}")

print()

# Kiểm tra số classes có khớp không
if "rf_model.pkl" in pickle_info and "classes.pkl" in pickle_info:
    rf_classes = pickle_info["rf_model.pkl"]
    pkl_classes = pickle_info["classes.pkl"]
    
    if rf_classes == pkl_classes:
        print(f"✅ Số classes trong rf_model và classes.pkl khớp nhau: {rf_classes}")
    else:
        print(f"❌ XUNG ĐỘT: rf_model có {rf_classes} classes, classes.pkl có {pkl_classes} classes")

print()
print()

# 5. Kiểm tra majors.json
print("5️⃣  KIỂM TRA MAJORS.JSON")
print("-" * 80)

majors_path = models_dir / "majors.json"
if majors_path.exists():
    try:
        with open(majors_path, 'r', encoding='utf-8') as f:
            majors = json.load(f)
        
        n_majors = len(majors)
        print(f"✅ majors.json hợp lệ")
        print(f"   Tổng số ngành: {n_majors}")
        print(f"   5 ngành đầu: {list(majors.keys())[:5]}")
        
        # Kiểm tra số lượng ngành
        if n_majors == 73:
            print(f"   ✅ Có 73 ngành (phiên bản mới - 400 mẫu/ngành)")
        elif n_majors < 73:
            print(f"   ⚠️  Chỉ có {n_majors} ngành (có thể là phiên bản cũ)")
    
    except Exception as e:
        print(f"❌ Lỗi đọc majors.json: {e}")

print()
print()

# 6. Tóm tắt xung đột
print("6️⃣  TÓM TẮT XUNG ĐỘT")
print("-" * 80)

conflicts = []

# Kiểm tra file cũ/mới
if timestamps and time_diff > 3600:
    conflicts.append("⚠️  Có file cũ không khớp với file mới")

# Kiểm tra xung đột classes
if "rf_model.pkl" in pickle_info and "classes.pkl" in pickle_info:
    if pickle_info["rf_model.pkl"] != pickle_info["classes.pkl"]:
        conflicts.append("❌ Số classes trong rf_model và classes.pkl không khớp")

# Kiểm tra file thiếu
missing_files = [f for f, exists in file_status.items() if not exists]
if missing_files:
    conflicts.append(f"❌ Thiếu file: {', '.join(missing_files)}")

if conflicts:
    print("PHÁT HIỆN XUNG ĐỘT:")
    for conflict in conflicts:
        print(f"  {conflict}")
else:
    print("✅ KHÔNG CÓ XUNG ĐỘT - Tất cả file model đều hợp lệ và khớp nhau")

print()
print("="*80)
print("KẾT THÚC KIỂM TRA")
print("="*80)
