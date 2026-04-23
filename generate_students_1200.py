import csv
import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
MAJORS_PATH = BASE / "models" / "majors.json"
OUT_PATH = BASE / "data" / "raw" / "students.csv"

random.seed(42)
majors = json.loads(MAJORS_PATH.read_text(encoding="utf-8"))

GROUPS = {
    "Cong nghe - Ky thuat": {
        "so_thich_chinh": ["Cong nghe"],
        "mon_hoc_yeu_thich": ["Tin hoc", "Toan", "Ly"],
        "ky_nang_noi_bat": ["Phan tich du lieu", "Giai quyet van de", "Tu duy logic", "Can than"],
        "tinh_cach": ["Ky luat", "Ti mi", "Quyet doan", "Ban linh"],
        "moi_truong_lam_viec_mong_muon": ["Ky thuat", "Nha may", "Van phong"],
        "muc_tieu_nghe_nghiep": ["Thu nhap cao", "On dinh"],
    },
    "Kinh doanh - Tai chinh - Quan tri": {
        "so_thich_chinh": ["Kinh doanh"],
        "mon_hoc_yeu_thich": ["Toan", "Van", "Anh"],
        "ky_nang_noi_bat": ["Lanh dao", "Giao tiep", "Sang tao", "Thuyet trinh"],
        "tinh_cach": ["Nang dong", "Quyet doan", "Trach nhiem"],
        "moi_truong_lam_viec_mong_muon": ["Van phong", "Linh hoat"],
        "muc_tieu_nghe_nghiep": ["Thu nhap cao", "Khoi nghiep", "On dinh"],
    },
    "Xa hoi - Nhan van - Giao duc - Luat": {
        "so_thich_chinh": ["Ngon ngu", "Giao duc", "Phap ly"],
        "mon_hoc_yeu_thich": ["Van", "Anh", "Su", "Dia"],
        "ky_nang_noi_bat": ["Giao tiep", "Thuyet trinh", "Lap luan", "Tu duy logic"],
        "tinh_cach": ["Kien nhan", "Trach nhiem", "Ky luat", "Huong ngoai", "Huong noi"],
        "moi_truong_lam_viec_mong_muon": ["Truong hoc", "Van phong"],
        "muc_tieu_nghe_nghiep": ["On dinh", "Cong hien xa hoi", "Trai nghiem quoc te"],
    },
    "Suc khoe - Dich vu cong dong": {
        "so_thich_chinh": ["Y te"],
        "mon_hoc_yeu_thich": ["Sinh", "Hoa", "Toan"],
        "ky_nang_noi_bat": ["Can than", "Kien nhan", "Trach nhiem", "Giai quyet van de"],
        "tinh_cach": ["Kien nhan", "Trach nhiem", "Ky luat", "Ti mi"],
        "moi_truong_lam_viec_mong_muon": ["Benh vien", "Phong thi nghiem", "Nha thuoc", "Cong dong"],
        "muc_tieu_nghe_nghiep": ["On dinh", "Cong hien xa hoi"],
    },
    "Sang tao - Truyen thong - Du lich - Kien truc": {
        "so_thich_chinh": ["Sang tao", "Du lich"],
        "mon_hoc_yeu_thich": ["Van", "Anh", "Toan"],
        "ky_nang_noi_bat": ["Sang tao", "Giao tiep", "Thuyet trinh", "Lanh dao"],
        "tinh_cach": ["Nang dong", "Huong ngoai", "Quyet doan", "Ti mi"],
        "moi_truong_lam_viec_mong_muon": ["Sang tao", "Linh hoat", "Van phong"],
        "muc_tieu_nghe_nghiep": ["Theo dam me", "Trai nghiem quoc te", "Khoi nghiep"],
    },
    "Khoa hoc xa hoi - lich su - dia ly": {
        "so_thich_chinh": ["Giao duc", "Phap ly", "Ngon ngu"],
        "mon_hoc_yeu_thich": ["Su", "Dia", "Van"],
        "ky_nang_noi_bat": ["Lap luan", "Giao tiep", "Phan tich", "Thuyet trinh"],
        "tinh_cach": ["Kien nhan", "Trach nhiem", "Ky luat", "Huong ngoai", "Huong noi"],
        "moi_truong_lam_viec_mong_muon": ["Truong hoc", "Van phong", "Linh hoat"],
        "muc_tieu_nghe_nghiep": ["On dinh", "Cong hien xa hoi", "Trai nghiem quoc te"],
    },
    "Khoa hoc tu nhien - hoa hoc - moi truong": {
        "so_thich_chinh": ["Y te", "Cong nghe"],
        "mon_hoc_yeu_thich": ["Hoa", "Sinh", "Toan"],
        "ky_nang_noi_bat": ["Can than", "Phan tich", "Giai quyet van de", "Tu duy logic"],
        "tinh_cach": ["Ti mi", "Ky luat", "Trach nhiem", "Kien nhan"],
        "moi_truong_lam_viec_mong_muon": ["Phong thi nghiem", "Benh vien", "Ky thuat"],
        "muc_tieu_nghe_nghiep": ["On dinh", "Cong hien xa hoi", "Phat trien chuyen mon"],
    },
}

KEYWORDS = {
    "Cong nghe - Ky thuat": ["phan tich", "lap trinh", "he thong", "du lieu", "ky thuat", "bao tri", "tinh toan"],
    "Kinh doanh - Tai chinh - Quan tri": ["quan ly", "ban hang", "thi truong", "tai chinh", "kinh doanh", "thuong mai", "chien luoc"],
    "Xa hoi - Nhan van - Giao duc - Luat": ["giao tiep", "ngon ngu", "luat", "giang day", "tam ly", "truyen thong", "phien dich", "lich su", "dia ly"],
    "Suc khoe - Dich vu cong dong": ["cham soc", "benh nhan", "y te", "xet nghiem", "phuc hoi", "dieu tri", "cong dong"],
    "Sang tao - Truyen thong - Du lich - Kien truc": ["sang tao", "thiet ke", "du lich", "khong gian", "media", "su kien", "phim", "quay phim", "dung phim", "dien anh"],
    "Khoa hoc xa hoi - lich su - dia ly": ["lich su", "dia ly", "xa hoi", "su pham", "luat", "giao duc", "ngon ngu"],
    "Khoa hoc tu nhien - hoa hoc - moi truong": ["hoa hoc", "moi truong", "sinh hoc", "thi nghiem", "duoc", "y te", "cong nghe"],
}

PROFILE_PREFIX = {
    "Cong nghe - Ky thuat": "Em quan tam den cong nghe va thuong thich",
    "Kinh doanh - Tai chinh - Quan tri": "Em quan tam den kinh doanh va thuong thich",
    "Xa hoi - Nhan van - Giao duc - Luat": "Em quan tam den giao duc, ngon ngu va thuong thich",
    "Suc khoe - Dich vu cong dong": "Em quan tam den y te va thuong thich",
    "Sang tao - Truyen thong - Du lich - Kien truc": "Em quan tam den sang tao va thuong thich",
    "Khoa hoc xa hoi - lich su - dia ly": "Em quan tam den lich su, dia ly va thuong thich",
    "Khoa hoc tu nhien - hoa hoc - moi truong": "Em quan tam den hoa hoc va thuong thich",
}

FUTURE_PREFIX = {
    "Cong nghe - Ky thuat": "Em muon phat trien trong linh vuc ky thuat va cong nghe ben vung.",
    "Kinh doanh - Tai chinh - Quan tri": "Em muon phat trien trong linh vuc kinh doanh va quan tri ben vung.",
    "Xa hoi - Nhan van - Giao duc - Luat": "Em muon phat trien trong linh vuc xa hoi va giao duc ben vung.",
    "Suc khoe - Dich vu cong dong": "Em muon phat trien trong linh vuc suc khoe va dich vu cong dong ben vung.",
    "Sang tao - Truyen thong - Du lich - Kien truc": "Em muon phat trien trong linh vuc sang tao va dich vu ben vung.",
    "Khoa hoc xa hoi - lich su - dia ly": "Em muon phat trien trong linh vuc lich su, dia ly va giao duc ben vung.",
    "Khoa hoc tu nhien - hoa hoc - moi truong": "Em muon phat trien trong linh vuc hoa hoc va moi truong ben vung.",
}

rows = []
for item in majors:
    major = item["nganh"]
    group = next((g for g in GROUPS if any(k in major.lower() for k in KEYWORDS[g])), None)
    if group is None:
        group = random.choice(list(GROUPS.keys()))
    tpl = GROUPS[group]
    for i in range(20):
        so_thich = random.choice(tpl["so_thich_chinh"])
        mon = random.choice(tpl["mon_hoc_yeu_thich"])
        skill = random.choice(tpl["ky_nang_noi_bat"])
        tinh_cach = random.choice(tpl["tinh_cach"])
        env = random.choice(tpl["moi_truong_lam_viec_mong_muon"])
        target = random.choice(tpl["muc_tieu_nghe_nghiep"])
        keyword = random.choice(KEYWORDS[group])
        profile_major = "quay phim va dung phim" if major == "Quay phim - Dung phim" else major.lower()
        profile = f"{PROFILE_PREFIX[group]} {keyword} va thuc hanh du an lien quan den {profile_major}."
        future_major = "quay phim va dung phim" if major == "Quay phim - Dung phim" else major.lower()
        future = f"{FUTURE_PREFIX[group]} Em dinh huong se lam viec voi {future_major} trong tuong lai."
        if i % 3 == 0:
            profile += " Em cung muon hoc hoi them qua du an thuc te va tu nghien cuu."
        if i % 4 == 0:
            future += " Em muon nang cao ky nang chuyen mon va lam viec nhom tot hon."
        rows.append([so_thich, mon, skill, tinh_cach, env, target, profile, future, major])

with OUT_PATH.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["so_thich_chinh","mon_hoc_yeu_thich","ky_nang_noi_bat","tinh_cach","moi_truong_lam_viec_mong_muon","muc_tieu_nghe_nghiep","mo_ta_ban_than","dinh_huong_tuong_lai","nganh_phu_hop"])
    writer.writerows(rows)

print(f"wrote {len(rows)} rows to {OUT_PATH}")
