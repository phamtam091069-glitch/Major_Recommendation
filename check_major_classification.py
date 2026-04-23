#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra toàn bộ các ngành xem đã được xếp vào nhóm ngành chưa
"""

import json
import sys
import io
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.constants import MAJOR_DISPLAY, MAJOR_PERSONALITY_REQUIREMENTS, SUGGESTION_VI

BASE_DIR = Path(__file__).resolve().parent

def load_majors():
    """Load danh sách ngành từ majors.json"""
    majors_path = BASE_DIR / "models" / "majors.json"
    with open(majors_path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_major_classification():
    """Kiểm tra phân loại ngành"""
    majors = load_majors()
    major_names = [m["nganh"] for m in majors]
    
    print("=" * 100)
    print("KIỂM TRA PHÂN LOẠI TOÀN BỘ CÁC NGÀNH")
    print("=" * 100)
    print()
    
    # Danh sách các nhóm kiểm tra
    groups = {
        "MAJOR_DISPLAY": MAJOR_DISPLAY,
        "MAJOR_PERSONALITY_REQUIREMENTS": MAJOR_PERSONALITY_REQUIREMENTS,
        "SUGGESTION_VI": SUGGESTION_VI,
    }
    
    # Tạo bảng kiểm tra
    print(f"📊 TỔNG SỐ NGÀNH TRONG MAJORS.JSON: {len(major_names)}")
    print()
    
    # Kiểm tra từng nhóm
    missing_by_group = {}
    for group_name, group_dict in groups.items():
        group_keys = set(group_dict.keys())
        missing = [m for m in major_names if m not in group_keys]
        missing_by_group[group_name] = missing
        
        print(f"📋 {group_name}:")
        print(f"   ✅ Có: {len(group_keys)} ngành")
        print(f"   ❌ Thiếu: {len(missing)} ngành")
        if missing:
            print(f"   Các ngành thiếu: {', '.join(missing)}")
        print()
    
    # Kiểm tra chi tiết từng ngành
    print("=" * 100)
    print("CHI TIẾT PHÂN LOẠI TỪNG NGÀNH")
    print("=" * 100)
    print()
    
    # Tạo DataFrame-like output
    print(f"{'STT':<4} | {'Ngành':<50} | DISPLAY | PERSONALITY | SUGGESTION")
    print("-" * 130)
    
    incomplete_majors = []
    
    for idx, major in enumerate(major_names, 1):
        has_display = "✅" if major in MAJOR_DISPLAY else "❌"
        has_personality = "✅" if major in MAJOR_PERSONALITY_REQUIREMENTS else "❌"
        has_suggestion = "✅" if major in SUGGESTION_VI else "❌"
        
        status = f"{has_display} | {has_personality:<11} | {has_suggestion}"
        
        # Đánh dấu ngành chưa hoàn thiện
        if has_display == "❌" or has_personality == "❌" or has_suggestion == "❌":
            incomplete_majors.append(major)
            status_marker = "⚠️ "
        else:
            status_marker = "✓ "
        
        print(f"{status_marker}{idx:<2} | {major:<50} | {status}")
    
    print()
    print("=" * 100)
    print("TÓM TẮT")
    print("=" * 100)
    print()
    
    total_majors = len(major_names)
    complete_majors = total_majors - len(incomplete_majors)
    
    print(f"📈 Tổng ngành: {total_majors}")
    print(f"✅ Ngành hoàn thiện (có đầy đủ 3 nhóm): {complete_majors} ({complete_majors*100//total_majors}%)")
    print(f"❌ Ngành chưa hoàn thiện: {len(incomplete_majors)} ({len(incomplete_majors)*100//total_majors}%)")
    print()
    
    if incomplete_majors:
        print("🔴 NGÀNH CHƯA HOÀN THIỆN:")
        print()
        for major in incomplete_majors:
            has_display = "✅" if major in MAJOR_DISPLAY else "❌"
            has_personality = "✅" if major in MAJOR_PERSONALITY_REQUIREMENTS else "❌"
            has_suggestion = "✅" if major in SUGGESTION_VI else "❌"
            
            missing_info = []
            if has_display == "❌":
                missing_info.append("MAJOR_DISPLAY (tên tiếng Việt)")
            if has_personality == "❌":
                missing_info.append("MAJOR_PERSONALITY_REQUIREMENTS (yêu cầu tính cách)")
            if has_suggestion == "❌":
                missing_info.append("SUGGESTION_VI (gợi ý)")
            
            print(f"   ❌ {major}")
            print(f"      Thiếu: {', '.join(missing_info)}")
        print()
    
    # Kiểm tra duplicates
    print("=" * 100)
    print("KIỂM TRA TRÙNG LẶP")
    print("=" * 100)
    print()
    
    # Check duplicates in MAJOR_DISPLAY
    display_values = list(MAJOR_DISPLAY.values())
    display_duplicates = [v for v in set(display_values) if display_values.count(v) > 1]
    
    if display_duplicates:
        print(f"⚠️ MAJOR_DISPLAY có {len(display_duplicates)} giá trị trùng lặp:")
        for dup in display_duplicates:
            keys = [k for k, v in MAJOR_DISPLAY.items() if v == dup]
            print(f"   • '{dup}' <- {keys}")
        print()
    else:
        print("✅ MAJOR_DISPLAY: không có giá trị trùng lặp")
        print()
    
    # Check keys in MAJOR_DISPLAY that not in majors
    extra_in_display = set(MAJOR_DISPLAY.keys()) - set(major_names)
    if extra_in_display:
        print(f"⚠️ MAJOR_DISPLAY có {len(extra_in_display)} ngành không có trong majors.json:")
        for extra in sorted(extra_in_display):
            print(f"   • {extra}")
        print()
    else:
        print("✅ MAJOR_DISPLAY: tất cả ngành có trong majors.json")
        print()
    
    # Tổng kết
    print("=" * 100)
    print("KẾT LUẬN")
    print("=" * 100)
    print()
    
    if len(incomplete_majors) == 0 and len(extra_in_display) == 0 and len(display_duplicates) == 0:
        print("✅ TẤT CẢ CÁC NGÀNH ĐÃ ĐƯỢC PHÂN LOẠI ĐẦY ĐỦ!")
    else:
        print(f"⚠️ CẦN XỬ LÝ {len(incomplete_majors) + len(extra_in_display) + len(display_duplicates)} VẤN ĐỀ")
        if incomplete_majors:
            print(f"   - {len(incomplete_majors)} ngành chưa hoàn thiện")
        if extra_in_display:
            print(f"   - {len(extra_in_display)} ngành trong MAJOR_DISPLAY không có trong majors.json")
        if display_duplicates:
            print(f"   - {len(display_duplicates)} giá trị trùng lặp trong MAJOR_DISPLAY")
    
    print()

if __name__ == "__main__":
    check_major_classification()
