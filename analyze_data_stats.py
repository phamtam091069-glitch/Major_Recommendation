import csv
import json
from collections import defaultdict
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Đọc dữ liệu
csv_path = 'data/raw/students.csv'
majors_json_path = 'models/majors.json'

# Thống kê theo ngành
major_count = defaultdict(int)
total_rows = 0

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_rows += 1
        major = row['nganh_phu_hop']
        major_count[major] += 1

# Đọc danh sách ngành từ model
with open(majors_json_path, 'r', encoding='utf-8') as f:
    majors_list = json.load(f)

# Tạo mapping ngành để phân loại
major_groups = {
    'Công nghệ & Điện tử': ['Cong nghe thong tin', 'Ky thuat phan mem', 'Khoa hoc du lieu', 'Tri tue nhan tao', 
                            'An ninh mang', 'He thong thong tin', 'Ky thuat may tinh', 'Ky thuat dien dien tu', 'Tu dong hoa'],
    'Kỹ thuật & Xây dựng': ['Ky thuat co khi', 'Ky thuat o to', 'Ky thuat xay dung', 'Cong nghe thuc pham',
                           'Dieu khien va quan ly tau bien', 'Khai thac may tau thuy va quan ly ky thuat', 'Dia ly hoc'],
    'Kinh doanh & Tài chính': ['Quan tri kinh doanh', 'Marketing', 'Thuong mai dien tu', 'Tai chinh ngan hang',
                              'Ke toan', 'Kiem toan', 'Logistics va quan ly chuoi cung ung', 'Quan tri nhan luc',
                              'Kinh doanh quoc te', 'Khoi nghiep va doi moi sang tao'],
    'Du lịch & Dịch vụ': ['Quan tri khach san', 'Quan tri nha hang va dich vu an uong', 'Du lich',
                         'Quan tri dich vu du lich va lu hanh', 'Huong dan du lich', 'Quan ly cang va logistics'],
    'Ngôn ngữ & Truyền thông': ['Ngon ngu Anh', 'Ngon ngu Trung', 'Ngon ngu Nhat', 'Ngon ngu Han',
                               'Bao chi', 'Truyen thong da phuong tien', 'Quan he cong chung'],
    'Pháp lý': ['Luat', 'Luat kinh te'],
    'Khoa học xã hội': ['Tam ly hoc', 'Cong tac xa hoi'],
    'Sư phạm & Giáo dục': ['Su pham Toan hoc', 'Su pham Tin hoc', 'Su pham Sinh hoc', 'Su pham Hoa hoc',
                          'Su pham Vat ly', 'Su pham Lich su', 'Su pham Dia ly', 'Su pham Giao duc the chat'],
    'Y tế & Chăm sóc sức khỏe': ['Y da khoa', 'Duoc hoc', 'Dieu duong', 'Ky thuat xet nghiem y hoc',
                                'Ky thuat hinh anh y hoc', 'Y hoc co truyen', 'Rang ham mat', 'Dinh duong',
                                'Y te cong cong', 'Ho sinh', 'Vat ly tri lieu va phuc hoi chuc nang'],
    'Nghệ thuật & Thiết kế': ['Thiet ke do hoa', 'Thiet ke thoi trang', 'Thiet ke noi that', 'Kien truc',
                             'My thuat', 'Nhiep anh', 'Quay phim - Dung phim', 'Thiet ke game', 'Nghe thuat so'],
    'Môi trường & Khoa học': ['Khoa hoc moi truong'],
    'Thể thao': ['Quan ly the thao']
}

# In kết quả
print("=" * 80)
print("THỐNG KÊ DỮ LIỆU HỆ THỐNG TƯ VẤN NGÀNH HỌC")
print("=" * 80)
print(f"\n📊 TỔNG SỐ MẪU DỮ LIỆU: {total_rows:,} mẫu\n")

# Thống kê theo nhóm ngành
print("=" * 80)
print("PHÂN BỐ THEO NHÓM NGÀNH")
print("=" * 80)

group_stats = {}
for group_name, majors in major_groups.items():
    group_total = sum(major_count.get(m, 0) for m in majors)
    group_stats[group_name] = group_total
    print(f"\n{group_name}: {group_total} mẫu")
    for major in majors:
        count = major_count.get(major, 0)
        percentage = (count / total_rows * 100) if total_rows > 0 else 0
        print(f"  • {major}: {count} mẫu ({percentage:.1f}%)")

# Thống kê từng ngành
print("\n" + "=" * 80)
print("CHI TIẾT TỪNG NGÀNH (sắp xếp theo số mẫu)")
print("=" * 80)

sorted_majors = sorted(major_count.items(), key=lambda x: x[1], reverse=True)
for rank, (major, count) in enumerate(sorted_majors, 1):
    percentage = (count / total_rows * 100) if total_rows > 0 else 0
    print(f"{rank:2d}. {major:40s}: {count:4d} mẫu ({percentage:5.1f}%)")

# Thống kê nhóm
print("\n" + "=" * 80)
print("TÓNG TẮT NHÓM NGÀNH")
print("=" * 80)

sorted_groups = sorted(group_stats.items(), key=lambda x: x[1], reverse=True)
for group, count in sorted_groups:
    percentage = (count / total_rows * 100) if total_rows > 0 else 0
    print(f"{group:35s}: {count:4d} mẫu ({percentage:5.1f}%)")

print("\n" + "=" * 80)
print(f"TỔNG CỘNG: {total_rows:,} mẫu | {len(major_count)} ngành được đại diện")
print("=" * 80)
