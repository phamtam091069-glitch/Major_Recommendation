"""
Script: Thêm dữ liệu cho sở thích "Kỹ thuật" và 2 ngành hàng hải
Mục đích: Tạo ~150 mẫu cho "Ky thuat" với 2 ngành hàng hải trong danh sách phù hợp
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Config
DATA_PATH = Path("data/raw/students.csv")
SAMPLES_PER_MAJOR = 150
TECHNICAL_MAJORS = [
    "Cong nghe thong tin",
    "Ky thuat phan mem",
    "Ky thuat co khi",
    "Ky thuat dien dien tu",
    "Ky thuat may tinh",
    "Tu dong hoa",
    "Dieu khien va quan ly tau bien",
    "Khai thac may tau thuy va quan ly ky thuat",
]

# Đọc dữ liệu hiện tại
print("[*] Reading current data...")
df = pd.read_csv(DATA_PATH)
print(f"   Total rows: {len(df)}")
print(f"   Columns: {df.columns.tolist()}")

# Kiểm tra xem "Ky thuat" đã có chưa
if "Ky thuat" in df["so_thich_chinh"].values:
    print("   [!] 'Ky thuat' already exists in data")
    ky_thuat_count = len(df[df["so_thich_chinh"] == "Ky thuat"])
    print(f"   Count: {ky_thuat_count} samples")
else:
    print("   [+] 'Ky thuat' not found, will create new")

# Lấy mẫu từ các ngành kỹ thuật khác để làm template
print(f"\n[*] Creating {SAMPLES_PER_MAJOR} samples for 'Ky thuat'...")
tech_df = df[df["so_thich_chinh"].isin(["Cong nghe", "Cong nghe thong tin"])]
print(f"   Found {len(tech_df)} template samples")

new_rows = []
for i in range(SAMPLES_PER_MAJOR):
    # Random chọn một template
    template = tech_df.sample(1).iloc[0].copy()
    
    # Thay đổi sở thích chính
    template["so_thich_chinh"] = "Ky thuat"
    
    # Gán ngành phù hợp từ TECHNICAL_MAJORS
    template["nganh_phu_hop"] = np.random.choice(TECHNICAL_MAJORS)
    
    # Random các trường khác để tăng tính đa dạng
    skills = ["Phân tích dữ liệu", "Tư duy logic", "Giải quyết vấn đề", "Sáng tạo", "Cẩn thận"]
    personality = ["Tỉ mỉ", "Kỷ luật", "Quyết đoán", "Trách nhiệm", "Năng động"]
    subjects = ["Toán", "Tin học", "Lý", "Hóa"]
    
    template["ky_nang_noi_bat"] = np.random.choice(skills)
    template["tinh_cach"] = np.random.choice(personality)
    template["mon_hoc_yeu_thich"] = np.random.choice(subjects)
    template["moi_truong_lam_viec_mong_muon"] = "Kỹ thuật"
    template["muc_tieu_nghe_nghiep"] = np.random.choice(["Phát triển chuyên môn", "Theo đam mê"])
    
    new_rows.append(template)

# Tạo DataFrame từ các dòng mới
new_df = pd.DataFrame(new_rows)
print(f"   [+] Created {len(new_df)} new samples")

# Gộp với dữ liệu cũ
print(f"\n[*] Merging data...")
df_combined = pd.concat([df, new_df], ignore_index=True)
print(f"   Total rows before: {len(df)}")
print(f"   Total rows after: {len(df_combined)}")

# Kiểm tra sự phân bố
print(f"\n[*] Distribution of so_thich_chinh:")
print(df_combined["so_thich_chinh"].value_counts())

# Lưu lại
print(f"\n[*] Saving data...")
df_combined.to_csv(DATA_PATH, index=False)
print(f"   [+] Saved successfully to {DATA_PATH}")

print(f"\n[OK] Done!")
print(f"   - Added {len(new_df)} 'Ky thuat' samples")
print(f"   - 2 marine majors added to suitable list")
print(f"   - Next step: run 'python train_model.py'")
