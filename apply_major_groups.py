"""
Script: Apply new MAJOR_GROUPS from MAJOR_GROUPS_NEW.txt to app.py
"""

import re

# Đọc app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Đọc file mới
with open('MAJOR_GROUPS_NEW.txt', 'r', encoding='utf-8') as f:
    new_groups = f.read()

# Tìm vị trí MAJOR_GROUPS trong app.py
start_idx = app_content.find('MAJOR_GROUPS = {')
end_idx = app_content.find('\n}', start_idx) + 2

if start_idx == -1:
    print("[ERROR] Could not find MAJOR_GROUPS in app.py")
    exit(1)

# Thay thế old groups bằng new groups
# Lưu ý: convert "Cong nghe - Ky thuat" từ new groups thành "Công nghệ - Kỹ thuật"
translations = {
    "Cong nghe - Ky thuat": "Công nghệ - Kỹ thuật",
    "Kinh doanh - Tai chinh - Quan tri": "Kinh doanh - Tài chính - Quản trị",
    "Xa hoi - Nhan van - Giao duc - Luat": "Xã hội - Nhân văn - Giáo dục - Luật",
    "Suc khoe - Dich vu cong dong": "Sức khỏe - Dịch vụ cộng đồng",
    "Sang tao - Truyen thong - Du lich - Kien truc": "Sáng tạo - Truyền thông - Du lịch - Kiến trúc",
}

# Áp dụng translation
translated_groups = new_groups
for old_text, new_text in translations.items():
    translated_groups = translated_groups.replace(f'"{old_text}"', f'"{new_text}"')

# Thay thế trong app content
old_section = app_content[start_idx:end_idx]
new_section = translated_groups

updated_content = app_content.replace(old_section, new_section)

# Lưu lại
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("[OK] Successfully updated app.py with new MAJOR_GROUPS")
print(f"[OK] Replaced {len(old_section)} characters")
