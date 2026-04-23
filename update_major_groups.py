"""
Script: Cap nhat MAJOR_GROUPS trong app.py voi tat ca nganh tu majors.json
Muc dich: Duasom nganh con thieu vao MAJOR_GROUPS voi phan loai dung
"""

import json
import re

# Doc majors.json
with open('models/majors.json', 'r', encoding='utf-8') as f:
    majors_list = json.load(f)

# Tao mapping moi
new_major_groups = {}

# Phan loai cac nganh theo loai
for item in majors_list:
    major = item['nganh']
    mo_ta = item['mo_ta'].lower()
    
    # Ky thuat + Hang hai (nhung khong phai y te)
    if ('ky thuat' in major.lower() and 'xet nghiem' not in major.lower() and 'hinh anh' not in major.lower()) or 'hang hai' in major.lower() or 'tau bien' in major.lower() or 'khai thac may' in major.lower() or 'tu dong hoa' in major.lower() or 'an ninh mang' in major.lower() or 'cong nghe thuc pham' in major.lower():
        group = "Cong nghe - Ky thuat"
    # Khoa hoc + Du lieu + AI
    elif 'khoa hoc du lieu' in major.lower() or 'tri tue nhan tao' in major.lower() or 'cong nghe thong tin' in major.lower() or 'he thong thong tin' in major.lower() or 'ky thuat may tinh' in major.lower() or 'ky thuat phan mem' in major.lower():
        group = "Cong nghe - Ky thuat"
    # Y te (gom ca xet nghiem, hinh anh y hoc)
    elif 'y da khoa' in major.lower() or 'duoc hoc' in major.lower() or 'dieu duong' in major.lower() or 'ky thuat xet nghiem' in major.lower() or 'ky thuat hinh anh y hoc' in major.lower() or 'rang ham mat' in major.lower() or 'dinh duong' in major.lower() or 'y hoc co truyen' in major.lower() or 'y te cong cong' in major.lower() or 'ho sinh' in major.lower() or 'vat ly tri lieu' in major.lower() or 'tam ly hoc' in major.lower():
        group = "Suc khoe - Dich vu cong dong"
    # Sang tao + Thiet ke + My thuat + Nhip anh
    elif 'thiet ke' in major.lower() or 'my thuat' in major.lower() or 'nhiep anh' in major.lower() or 'quay phim' in major.lower() or 'game' in major.lower() or 'kien truc' in major.lower() or 'nghe thuat so' in major.lower():
        group = "Sang tao - Truyen thong - Du lich - Kien truc"
    # Du lich + Quan ly dich vu + Hang hai dich vu
    elif 'du lich' in major.lower() or 'huong dan' in major.lower():
        group = "Sang tao - Truyen thong - Du lich - Kien truc"
    # Giao duc + Su pham + The chat
    elif 'su pham' in major.lower() or 'giao duc the chat' in major.lower():
        group = "Xa hoi - Nhan van - Giao duc - Luat"
    # Kinh doanh + Tai chinh + Quan tri
    elif 'quan tri' in major.lower() or 'marketing' in major.lower() or 'thuong mai' in major.lower() or 'tai chinh' in major.lower() or 'ke toan' in major.lower() or 'kiem toan' in major.lower() or 'kinh doanh' in major.lower() or 'khoi nghiep' in major.lower():
        group = "Kinh doanh - Tai chinh - Quan tri"
    # Logistics + Quan ly hang
    elif 'logistics' in major.lower() or 'quan ly cang' in major.lower():
        group = "Kinh doanh - Tai chinh - Quan tri"
    # Ngon ngu
    elif 'ngon ngu' in major.lower():
        group = "Xa hoi - Nhan van - Giao duc - Luat"
    # Truyền thông + Bao chi
    elif 'bao chi' in major.lower() or 'truyen thong' in major.lower() or 'quan he cong chung' in major.lower():
        group = "Sang tao - Truyen thong - Du lich - Kien truc"
    # Luat
    elif 'luat' in major.lower():
        group = "Xa hoi - Nhan van - Giao duc - Luat"
    # Cong tac + Moi truong
    elif 'cong tac xa hoi' in major.lower() or 'khoa hoc moi truong' in major.lower() or 'quan ly the thao' in major.lower():
        group = "Xa hoi - Nhan van - Giao duc - Luat"
    # Dia ly
    elif 'dia ly' in major.lower():
        group = "Xa hoi - Nhan van - Giao duc - Luat"
    # Default: Cong nghe
    else:
        group = "Cong nghe - Ky thuat"
    
    new_major_groups[major] = group

# Tao Python code va luu vao file
output_lines = []
output_lines.append("MAJOR_GROUPS = {")
for major, group in sorted(new_major_groups.items()):
    output_lines.append(f'    "{major}": "{group}",')
output_lines.append("}")

# Luu vao file
with open('MAJOR_GROUPS_NEW.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

# In summary
groups_summary = {}
for major, group in sorted(new_major_groups.items()):
    if group not in groups_summary:
        groups_summary[group] = []
    groups_summary[group].append(major)

print("[OK] Total: {} majors classified".format(len(new_major_groups)))
print("[OK] Output saved to MAJOR_GROUPS_NEW.txt")
for group in sorted(groups_summary.keys()):
    print("[{}] {} majors".format(group, len(groups_summary[group])))
