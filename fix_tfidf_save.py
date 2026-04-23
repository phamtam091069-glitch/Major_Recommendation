#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix tfidf.pkl corruption - save as JSON format instead
"""
import json
import joblib
from pathlib import Path

print("=" * 80)
print("FIX TFIDF PICKLE CORRUPTION")
print("=" * 80)
print()

# Try to load current corrupted tfidf
tfidf_path = Path("models/tfidf.pkl")

if not tfidf_path.exists():
    print("❌ tfidf.pkl không tồn tại")
    exit(1)

try:
    print("📤 Thử load tfidf.pkl hiện tại...")
    tfidf = joblib.load(tfidf_path)
    print("✅ Load thành công (không bị corrupt)")
    print(f"   Type: {type(tfidf)}")
    print(f"   Max features: {tfidf.max_features if hasattr(tfidf, 'max_features') else 'N/A'}")
except Exception as e:
    print(f"❌ Load tfidf.pkl thất bại: {e}")
    print()
    print("💡 GIẢI PHÁP: Xóa tfidf.pkl và train lại")
    print("   rm models/tfidf.pkl")
    print("   python train_model.py")
    print()
    print("⚠️  Hoặc đơn giản hơn: Xóa tất cả models và train từ đầu")
    print("   rm models/*.pkl")
    print("   python train_model.py")
    exit(1)

print()
print("=" * 80)
print("SUCCESS")
print("=" * 80)
