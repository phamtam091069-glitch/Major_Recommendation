#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra xem 2 ngành hàng hải có trong dữ liệu huấn luyện không
"""

import pandas as pd
import sys
import io
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

def check_marine_majors():
    """Kiểm tra ngành hàng hải trong dữ liệu"""
    
    # Đọc dữ liệu học sinh
    csv_path = BASE_DIR / "data" / "raw" / "students.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print("=" * 100)
    print("KIỂM TRA NGÀNH HÀNG HẢI TRONG DỮ LIỆU HUẤN LUYỆN")
    print("=" * 100)
    print()
    
    # 2 ngành hàng hải
    marine_majors = [
        "Dieu khien va quan ly tau bien",
        "Khai thac may tau thuy va quan ly ky thuat"
    ]
    
    print("📊 TỔNG SỐ HỌC SINH TRONG DỮ LIỆU:", len(df))
    print("📊 TỔNG SỐ NGÀNH TRONG DỮ LIỆU:", df['nganh_phu_hop'].nunique())
    print()
    
    # Kiểm tra từng ngành hàng hải
    for major in marine_majors:
        count = (df['nganh_phu_hop'] == major).sum()
        percentage = (count / len(df)) * 100 if len(df) > 0 else 0
        
        if count > 0:
            print(f"✅ {major}")
            print(f"   Số lượng: {count} học sinh ({percentage:.2f}%)")
        else:
            print(f"❌ {major}")
            print(f"   Không có dữ liệu")
        print()
    
    # Liệt kê tất cả các ngành trong dữ liệu
    print("=" * 100)
    print("DANH SÁCH TẤT CẢ CÁC NGÀNH TRONG DỮ LIỆU")
    print("=" * 100)
    print()
    
    major_counts = df['nganh_phu_hop'].value_counts().sort_values(ascending=False)
    
    for idx, (major, count) in enumerate(major_counts.items(), 1):
        percentage = (count / len(df)) * 100
        is_marine = "🚢" if major in marine_majors else "  "
        print(f"{is_marine} {idx:2d}. {major:<50} - {count:4d} ({percentage:5.2f}%)")
    
    print()
    print("=" * 100)
    print("KẾT LUẬN")
    print("=" * 100)
    print()
    
    marine_in_data = sum(1 for m in marine_majors if (df['nganh_phu_hop'] == m).sum() > 0)
    
    if marine_in_data == 2:
        print("✅ CẢ 2 NGÀNH HÀNG HẢI ĐÃ CÓ TRONG DỮ LIỆU HUẤN LUYỆN")
        print("   → Có thể train lại mô hình để nhận diện 2 ngành này")
    elif marine_in_data == 1:
        print("⚠️ CHỈ CÓ 1 NGÀNH HÀNG HẢI TRONG DỮ LIỆU")
        print("   → Cần thêm dữ liệu cho ngành còn lại")
    else:
        print("❌ KHÔNG CÓ NGÀNH HÀNG HẢI TRONG DỮ LIỆU")
        print("   → CẦN THÊM DỮ LIỆU MẪU CHO 2 NGÀNH NÀY TRƯỚC KHI TRAIN")
        print()
        print("🚀 ĐỀ XUẤT GIẢI PHÁP:")
        print("   1. Chạy: python data/generate_balanced_students.py")
        print("      → Tạo dữ liệu cân bằng với 2 ngành hàng hải")
        print("   2. Sau đó chạy: python train_model.py")
        print("      → Train lại mô hình với dữ liệu mới")
    
    print()

if __name__ == "__main__":
    check_marine_majors()
