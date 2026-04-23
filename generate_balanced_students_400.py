import csv
import json
import random
import hashlib
from collections import Counter
import unicodedata
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Các lựa chọn từ dữ liệu thực
so_thich_chinh_options = [
    'Cong nghe', 'Du lich', 'Y te', 'Nghe thuat', 'Kinh doanh', 
    'Giao duc', 'Ngon ngu', 'Phap ly'
]

mon_hoc_yeu_thich_options = [
    'Ly', 'Van', 'Toan', 'Anh', 'Hoa', 'Sinh', 'Su', 'Tin hoc', 'Dia'
]

ky_nang_noi_bat_options = [
    'Phan tich', 'Giao tiep', 'Sang tao', 'Thuyyet trinh', 'Kien nhan', 
    'Ky luat', 'Lanh dao', 'Tu duy khong gian', 'Giai quyet van de', 
    'Ban linh', 'Can than', 'Lap luan', 'Thong ke'
]

tinh_cach_options = [
    'Nang dong', 'Huong noi', 'Kien tri', 'Ban linh', 'Nang dong',
    'Huong ngoai', 'Ti mi', 'Kien nhan'
]

moi_truong_lam_viec_options = [
    'Linh hoat', 'Van phong', 'Ky thuat', 'Benh vien', 'Truong hoc', 'Sang tao'
]

muc_tieu_nghe_nghiep_options = [
    'Thu nhap cao', 'Cong hien xa hoi', 'Khoi nghiep', 'On dinh', 'Theo dam me'
]

# Các mẫu mô tả bản thân
mo_ta_templates = [
    "Em co xu huong tap trung vao {keyword1}, vi em thay linh vuc nay phu hop tinh cach.",
    "Ban than em yeu thich {keyword1}, va muon phat trien lau dai.",
    "Gan day em dau tu thoi gian cho {keyword1}, de tao gia tri thuc te cho cong viec.",
    "Em rat quan tam den {keyword1}, vi em thay linh vuc nay phu hop tinh cach.",
    "Em thuong tim hieu them ve {keyword1}, nham nang cao co hoi nghe nghiep sau nay.",
    "Em co xu huong tap trung vao {keyword1}, de tao gia tri thuc te cho cong viec.",
    "Em thich lam viec voi {keyword1}, de ket hop dam me voi nang luc cua minh.",
]

# Các mẫu định hướng
dinh_huong_templates = [
    "Trong 3-5 nam toi, em muon {target_action} trong linh vuc {major}.",
    "Muc tieu nghe nghiep cua em la {target_action} trong linh vuc {major}.",
    "Em dinh huong se {target_action} trong linh vuc {major}.",
    "Duong dai em mong muon {target_action} trong linh vuc {major}.",
]

# Các từ khóa cho mô tả
keywords_list = [
    "phan tich du lieu va tham gia ra quyet dinh",
    "thiet ke san pham tao ra giac tri",
    "lap trinh phat trien he thong",
    "giao tiep voi khach hang va doi tac",
    "quan ly du an va to chuc cong viec",
    "tim hieu cong nghe moi va xu dung vao thuc te",
    "dao tao va huong dan nhan vien",
    "tro thanh chuyen gia trong linh vuc",
    "sang tao va phat trien san pham",
    "thuc hien nghien cuu khoa hoc",
]

# Các target action
target_actions = [
    "lam", "tro thanh", "hoat dong trong", "phat trien", "khoi nghiep"
]

# Danh sách 74 ngành
majors_74 = [
    "Cong nghe thong tin", "Ky thuat phan mem", "Khoa hoc du lieu", "Tri tue nhan tao",
    "An ninh mang", "He thong thong tin", "Ky thuat may tinh", "Ky thuat dien dien tu",
    "Tu dong hoa", "Ky thuat co khi", "Ky thuat o to", "Ky thuat xay dung",
    "Cong nghe thuc pham", "Dieu khien va quan ly tau bien", "Khai thac may tau thuy va quan ly ky thuat",
    "Dia ly hoc", "Quan tri kinh doanh", "Marketing", "Thuong mai dien tu",
    "Tai chinh ngan hang", "Ke toan", "Kiem toan", "Logistics va quan ly chuoi cung ung",
    "Quan tri nhan luc", "Kinh doanh quoc te", "Khoi nghiep va doi moi sang tao",
    "Ngon ngu Anh", "Ngon ngu Trung", "Ngon ngu Nhat", "Ngon ngu Han",
    "Bao chi", "Truyen thong da phuong tien", "Quan he cong chung",
    "Luat", "Luat kinh te", "Tam ly hoc", "Cong tac xa hoi",
    "Su pham Toan hoc", "Su pham Tin hoc", "Su pham Sinh hoc", "Su pham Hoa hoc",
    "Su pham Vat ly", "Su pham Lich su", "Su pham Dia ly", "Su pham Giao duc the chat",
    "Y da khoa", "Duoc hoc", "Dieu duong", "Ky thuat xet nghiem y hoc",
    "Ky thuat hinh anh y hoc", "Y hoc co truyen", "Rang ham mat", "Dinh duong",
    "Y te cong cong", "Ho sinh", "Vat ly tri lieu va phuc hoi chuc nang",
    "Thiet ke do hoa", "Thiet ke thoi trang", "Thiet ke noi that", "Kien truc",
    "My thuat", "Nhiep anh", "Quay phim - Dung phim", "Thiet ke game",
    "Nghe thuat so", "Quan tri khach san", "Quan tri nha hang va dich vu an uong",
    "Du lich", "Quan tri dich vu du lich va lu hanh", "Huong dan du lich",
    "Khoa hoc moi truong", "Quan ly the thao", "Quan ly cang va logistics"
]

print("=" * 80)
print("GENERATING 29,600 BALANCED SYNTHETIC STUDENT DATA (400 per major)")
print("=" * 80)
print()

def generate_unique_description(major, seed_keywords, used_hashes):
    """Generate unique descriptions for students"""
    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        # Chọn template ngẫu nhiên
        template = random.choice(mo_ta_templates)
        keyword = random.choice(keywords_list + seed_keywords)
        
        # Tạo mô tả
        description = template.format(keyword1=keyword)
        
        # Kiểm tra trùng lặp
        desc_hash = hashlib.md5(description.encode()).hexdigest()
        if desc_hash not in used_hashes:
            used_hashes.add(desc_hash)
            return description
        
        attempts += 1
    
    # Fallback: tạo description khác
    return f"Em quan tam den {keyword} va muon phat trien trong linh vuc {major}."

def generate_orientation(major):
    """Generate orientation for students"""
    template = random.choice(dinh_huong_templates)
    action = random.choice(target_actions)
    return template.format(target_action=action, major=major)

# Tạo CSV
csv_path = 'data/raw/students_balanced_400.csv'
used_hashes = set()
generated_count = 0
total_to_generate = len(majors_74) * 400

print(f"Target: {total_to_generate:,} rows ({len(majors_74)} majors × 400 samples)\n")

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'so_thich_chinh', 'mon_hoc_yeu_thich', 'ky_nang_noi_bat', 'tinh_cach',
        'moi_truong_lam_viec_mong_muon', 'muc_tieu_nghe_nghiep',
        'mo_ta_ban_than', 'dinh_huong_tuong_lai', 'nganh_phu_hop'
    ])
    writer.writeheader()
    
    # Generate cho từng ngành
    for major_idx, major in enumerate(majors_74, 1):
        major_count = 0
        attempts_per_major = 0
        max_attempts = 500  # Tránh loop vô hạn
        
        while major_count < 400 and attempts_per_major < max_attempts:
            row = {
                'so_thich_chinh': random.choice(so_thich_chinh_options),
                'mon_hoc_yeu_thich': random.choice(mon_hoc_yeu_thich_options),
                'ky_nang_noi_bat': random.choice(ky_nang_noi_bat_options),
                'tinh_cach': random.choice(tinh_cach_options),
                'moi_truong_lam_viec_mong_muon': random.choice(moi_truong_lam_viec_options),
                'muc_tieu_nghe_nghiep': random.choice(muc_tieu_nghe_nghiep_options),
                'mo_ta_ban_than': generate_unique_description(major, keywords_list, used_hashes),
                'dinh_huong_tuong_lai': generate_orientation(major),
                'nganh_phu_hop': major
            }
            
            writer.writerow(row)
            major_count += 1
            generated_count += 1
            attempts_per_major += 1
            
            # Progress bar
            if generated_count % 500 == 0:
                progress = (generated_count / total_to_generate) * 100
                print(f"Progress: {generated_count:,}/{total_to_generate:,} ({progress:.1f}%)")
        
        print(f"✓ {major_idx:2d}. {major:45s} - {major_count:3d} samples")

print()
print("=" * 80)
print(f"COMPLETED: {generated_count:,} rows generated in '{csv_path}'")
print("=" * 80)

# Verify dữ liệu
print("\nVerifying data...")
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    major_count = Counter([row['nganh_phu_hop'] for row in rows])
    
    print(f"Total rows: {len(rows):,}")
    print(f"Total majors: {len(major_count)}")
    print(f"\nMajors with 400 samples:")
    count_400 = sum(1 for count in major_count.values() if count == 400)
    print(f"  {count_400}/{len(majors_74)} majors ✓")
    
    print(f"\nMajors statistics:")
    for major, count in sorted(major_count.items()):
        if count == 400:
            print(f"  {major:45s}: {count:3d} ✓")

print("\n✓ Data generation completed successfully!")
print(f"✓ File saved to: {csv_path}")
