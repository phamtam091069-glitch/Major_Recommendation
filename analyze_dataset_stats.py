#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phân tích thống kê dữ liệu huấn luyện
Đếm tổng số mẫu, số mẫu theo ngành, và theo nhóm lĩnh vực
"""

import sys
import csv
import json
from pathlib import Path
from collections import defaultdict

# Fix Unicode encoding on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn file
DATA_FILE = "data/raw/students.csv"
MAJORS_FILE = "models/majors.json"

# Phân nhóm ngành theo lĩnh vực
MAJOR_GROUPS = {
    "🖥️ Công nghệ & Điện tử": [
        "Cong nghe thong tin", "Ky thuat phan mem", "Khoa hoc du lieu",
        "Tri tue nhan tao", "An ninh mang", "He thong thong tin",
        "Ky thuat may tinh", "Ky thuat dien dien tu", "Tu dong hoa"
    ],
    "⚙️ Kỹ thuật & Xây dựng": [
        "Ky thuat co khi", "Ky thuat o to", "Ky thuat xay dung",
        "Cong nghe thuc pham", "Dieu khien va quan ly tau bien",
        "Khai thac may tau thuy va quan ly ky thuat", "Dia ly hoc"
    ],
    "💼 Kinh doanh & Tài chính": [
        "Quan tri kinh doanh", "Marketing", "Thuong mai dien tu",
        "Tai chinh ngan hang", "Ke toan", "Kiem toan",
        "Logistics va quan ly chuoi cung ung", "Quan tri nhan luc",
        "Kinh doanh quoc te", "Khoi nghiep va doi moi sang tao"
    ],
    "🏨 Du lịch & Dịch vụ": [
        "Quan tri khach san", "Quan tri nha hang va dich vu an uong",
        "Du lich", "Quan tri dich vu du lich va lu hanh",
        "Huong dan du lich", "Quan ly cang va logistics"
    ],
    "🗣️ Ngôn ngữ & Truyền thông": [
        "Ngon ngu Anh", "Ngon ngu Trung", "Ngon ngu Nhat", "Ngon ngu Han",
        "Bao chi", "Truyen thong da phuong tien", "Quan he cong chung"
    ],
    "⚖️ Pháp lý": [
        "Luat", "Luat kinh te"
    ],
    "🧠 Khoa học xã hội": [
        "Tam ly hoc", "Cong tac xa hoi"
    ],
    "📚 Sư phạm & Giáo dục": [
        "Su pham Toan hoc", "Su pham Tin hoc", "Su pham Sinh hoc",
        "Su pham Hoa hoc", "Su pham Vat ly", "Su pham Lich su",
        "Su pham Dia ly", "Su pham Giao duc the chat"
    ],
    "🏥 Y tế & Chăm sóc sức khỏe": [
        "Y da khoa", "Duoc hoc", "Dieu duong", "Ky thuat xet nghiem y hoc",
        "Ky thuat hinh anh y hoc", "Y hoc co truyen", "Rang ham mat",
        "Dinh duong", "Y te cong cong", "Ho sinh",
        "Vat ly tri lieu va phuc hoi chuc nang"
    ],
    "🎨 Nghệ thuật & Thiết kế": [
        "Thiet ke do hoa", "Thiet ke thoi trang", "Thiet ke noi that",
        "Kien truc", "My thuat", "Nhiep anh", "Quay phim - Dung phim",
        "Thiet ke game", "Nghe thuat so"
    ],
    "🌍 Môi trường & Khoa học": [
        "Khoa hoc moi truong"
    ],
    "⚽ Thể thao": [
        "Quan ly the thao"
    ]
}

def load_data():
    """Load dữ liệu từ CSV"""
    if not Path(DATA_FILE).exists():
        print(f"❌ File {DATA_FILE} không tồn tại")
        return []
    
    rows = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    return rows

def analyze_data(rows):
    """Phân tích dữ liệu"""
    total_samples = len(rows)
    major_counts = defaultdict(int)
    group_counts = {group: 0 for group in MAJOR_GROUPS.keys()}
    
    # Đếm mẫu theo ngành
    for row in rows:
        major = row.get("nganh_phu_hop", "Unknown")
        major_counts[major] += 1
        
        # Đếm theo nhóm
        for group, majors in MAJOR_GROUPS.items():
            if major in majors:
                group_counts[group] += 1
                break
    
    return total_samples, major_counts, group_counts

def format_report(total_samples, major_counts, group_counts):
    """Định dạng báo cáo"""
    report = []
    report.append("=" * 80)
    report.append("📊 THỐNG KÊ DỮ LIỆU HỆ THỐNG TƯ VẤN NGÀNH HỌC")
    report.append("=" * 80)
    report.append("")
    
    # Tổng số mẫu
    report.append(f"📌 TỔNG SỐ MẪU DỮ LIỆU: {total_samples}")
    report.append("")
    
    # Thống kê theo nhóm lĩnh vực
    report.append("-" * 80)
    report.append("📂 PHÂN BỐ THEO NHÓM LĨNH VỰC (Tổng 12 nhóm)")
    report.append("-" * 80)
    
    sorted_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    total_in_groups = 0
    
    for i, (group, count) in enumerate(sorted_groups, 1):
        percentage = (count / total_samples * 100) if total_samples > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        report.append(f"{i:2}. {group:40} | {count:4} mẫu | {percentage:5.1f}% | {bar}")
        total_in_groups += count
    
    report.append("")
    report.append(f"Tổng mẫu trong nhóm: {total_in_groups} / {total_samples}")
    report.append("")
    
    # Thống kê chi tiết theo ngành
    report.append("-" * 80)
    report.append(f"📋 CHI TIẾT THEO NGÀNH (Tổng {len(major_counts)} ngành)")
    report.append("-" * 80)
    
    sorted_majors = sorted(major_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (major, count) in enumerate(sorted_majors, 1):
        percentage = (count / total_samples * 100) if total_samples > 0 else 0
        bar_length = int(percentage / 0.5)
        bar = "█" * min(bar_length, 40)
        report.append(f"{i:3}. {major:45} | {count:4} mẫu | {percentage:5.1f}%")
    
    report.append("")
    
    # Thống kê cơ bản
    report.append("-" * 80)
    report.append("📈 THỐNG KÊ CƠ BẢN")
    report.append("-" * 80)
    
    counts = list(major_counts.values())
    if counts:
        report.append(f"Ngành có mẫu nhiều nhất: {sorted_majors[0][0]} ({sorted_majors[0][1]} mẫu)")
        report.append(f"Ngành có mẫu ít nhất:   {sorted_majors[-1][0]} ({sorted_majors[-1][1]} mẫu)")
        report.append(f"Trung bình mẫu/ngành:   {sum(counts) / len(counts):.1f} mẫu")
        report.append(f"Median mẫu/ngành:       {sorted(counts)[len(counts)//2]:.1f} mẫu")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def save_json_stats(total_samples, major_counts, group_counts):
    """Lưu thống kê dưới dạng JSON"""
    stats = {
        "total_samples": total_samples,
        "total_majors": len(major_counts),
        "total_groups": len(group_counts),
        "by_major": dict(sorted(major_counts.items(), key=lambda x: x[1], reverse=True)),
        "by_group": dict(sorted(group_counts.items(), key=lambda x: x[1], reverse=True))
    }
    
    with open("reports/data_distribution_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("✅ JSON stats saved to: reports/data_distribution_analysis.json")

def main():
    """Main function"""
    print("🔍 Đang phân tích dữ liệu...")
    
    rows = load_data()
    if not rows:
        print("❌ Không có dữ liệu để phân tích")
        return
    
    total_samples, major_counts, group_counts = analyze_data(rows)
    report = format_report(total_samples, major_counts, group_counts)
    
    print(report)
    
    # Lưu báo cáo
    with open("reports/data_distribution_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Báo cáo saved to: reports/data_distribution_report.txt")
    
    # Lưu JSON
    save_json_stats(total_samples, major_counts, group_counts)

if __name__ == "__main__":
    main()
