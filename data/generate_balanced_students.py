"""
Sinh du lieu synthetic cho bai toan goi y nganh:
- students.csv: tap train chinh (co controlled noise + hard negatives)
- students_holdout.csv: tap holdout rieng (template khac) de test tong quat hoa

Chay:
    python data/generate_balanced_students.py
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_TRAIN = RAW_DIR / "students.csv"
OUT_HOLDOUT = RAW_DIR / "students_holdout.csv"

ROWS_PER_MAJOR = 150
HOLDOUT_ROWS_PER_MAJOR = 50
NOISE_RATE = 0.45
HARD_NEGATIVE_RATE = 0.50

MAJORS_ORDER = [
    "Cong nghe thong tin",
    "Ky thuat phan mem",
    "Khoa hoc du lieu",
    "Tri tue nhan tao",
    "An ninh mang",
    "He thong thong tin",
    "Ky thuat may tinh",
    "Ky thuat dien dien tu",
    "Tu dong hoa",
    "Ky thuat co khi",
    "Ky thuat o to",
    "Ky thuat xay dung",
    "Quan tri kinh doanh",
    "Marketing",
    "Thuong mai dien tu",
    "Tai chinh ngan hang",
    "Ke toan",
    "Kiem toan",
    "Logistics va quan ly chuoi cung ung",
    "Quan tri nhan luc",
    "Kinh doanh quoc te",
    "Quan tri khach san",
    "Quan tri nha hang va dich vu an uong",
    "Khoi nghiep va doi moi sang tao",
    "Ngon ngu Anh",
    "Ngon ngu Trung",
    "Ngon ngu Nhat",
    "Ngon ngu Han",
    "Bao chi",
    "Truyen thong da phuong tien",
    "Quan he cong chung",
    "Luat",
    "Luat kinh te",
    "Tam ly hoc",
    "Cong tac xa hoi",
    "Su pham Toan hoc",
    "Su pham Tin hoc",
    "Su pham Sinh hoc",
    "Su pham Hoa hoc",
    "Su pham Vat ly",
    "Su pham Lich su",
    "Su pham Dia ly",
    "Y da khoa",
    "Duoc hoc",
    "Dieu duong",
    "Ky thuat xet nghiem y hoc",
    "Ky thuat hinh anh y hoc",
    "Y hoc co truyen",
    "Rang ham mat",
    "Dinh duong",
    "Y te cong cong",
    "Ho sinh",
    "Vat ly tri lieu va phuc hoi chuc nang",
    "Quan ly benh vien",
    "Thiet ke do hoa",
    "Thiet ke thoi trang",
    "Thiet ke noi that",
    "Kien truc",
    "My thuat",
    "Nhiếp anh",
    "Quay phim - Dung phim",
    "Du lich",
    "Quan tri dich vu du lich va lu hanh",
    "Huong dan du lich",
    "Thiet ke game",
    "Nghe thuat so",
    "Dieu khien va quan ly tau bien",
    "Khai thac may tau thuy va quan ly ky thuat",
    "Dia ly hoc",
    "Khoa hoc moi truong",
    "Cong nghe thuc pham",
]

TINH_OPTIONS = ["Huong noi", "Huong ngoai", "Ti mi", "Nang dong", "Kien nhan", "Kien tri", "Ban linh"]
MUC_OPTIONS = ["On dinh", "Thu nhap cao", "Theo dam me", "Khoi nghiep", "Cong hien xa hoi"]

PROFILE = {
    "Cong nghe thong tin": {
        "so": "Cong nghe",
        "mons": ["Tin hoc", "Toan", "Ly"],
        "skills": ["Phan tich", "Giai quyet van de", "Tu hoc"],
        "moi": ["Ky thuat", "Van phong", "Linh hoat"],
        "kw": [
            "lap trinh phan mem web API backend bao mat may tinh",
            "thuat toan cau truc du lieu he dieu hanh mang may tinh",
            "xay dung ung dung di dong va dich vu cloud",
            "tu dong hoa kiem thu va toi uu hieu nang he thong",
        ],
        "goal": "tro thanh ky su phan mem full stack hoac backend.",
    },
    "Khoa hoc du lieu": {
        "so": "Cong nghe",
        "mons": ["Toan", "Tin hoc", "Ly"],
        "skills": ["Phan tich", "Giai quyet van de", "Thong ke"],
        "moi": ["Van phong", "Ky thuat", "Linh hoat"],
        "kw": [
            "phan tich du lieu thong ke SQL dashboard visualization",
            "machine learning mo hinh du doan va bao cao kinh doanh",
            "Python pandas big data va kho du lieu",
            "tim insight tu so lieu va A B testing",
        ],
        "goal": "lam data analyst hoac data scientist trong doanh nghiep.",
    },
    "Quan tri kinh doanh": {
        "so": "Kinh doanh",
        "mons": ["Toan", "Van", "Anh"],
        "skills": ["Giao tiep", "Lanh dao", "Phan tich"],
        "moi": ["Van phong", "Linh hoat"],
        "kw": [
            "quan tri kinh doanh chien luoc lanh dao doanh nghiep",
            "lap ke hoach phat trien ban hang va doi ngu",
            "tu van quy trinh van hanh va toi uu hieu suat",
            "dieu phoi phong ban va ra quyet dinh theo du lieu",
        ],
        "goal": "quan ly bo phan hoac dieu hanh cong ty.",
    },
    "Marketing": {
        "so": "Kinh doanh",
        "mons": ["Van", "Anh", "Toan"],
        "skills": ["Sang tao", "Giao tiep", "Phan tich"],
        "moi": ["Sang tao", "Van phong", "Linh hoat"],
        "kw": [
            "marketing digital quang cao thuong hieu social media",
            "noi dung sang tao SEO growth va hanh vi khach hang",
            "campaign truyen thong influencer va branding",
            "nghien cuu thi truong va chien luoc tiep thi",
        ],
        "goal": "lam chuyen vien marketing digital va brand.",
    },
    "Thiet ke do hoa": {
        "so": "Nghe thuat",
        "mons": ["Van", "Tin hoc", "Anh", "Ly"],
        "skills": ["Sang tao", "Tham my", "Giao tiep"],
        "moi": ["Sang tao", "Van phong", "Linh hoat"],
        "kw": [
            "thiet ke do hoa mau sac poster branding illustrator",
            "UI UX giao dien sang tao my thuat so",
            "minh hoa motion graphic video ngan",
            "xay dung bo nhan dien thuong hieu da nen tang",
        ],
        "goal": "lam designer chuyen nghiep agency hoac freelance.",
    },
    "Dieu duong": {
        "so": "Y te",
        "mons": ["Sinh", "Van", "Hoa"],
        "skills": ["Can than", "Kien nhan", "Giao tiep"],
        "moi": ["Benh vien", "Linh hoat"],
        "kw": [
            "dieu duong cham soc benh nhan y te lam sang",
            "sinh hoc suc khoe ho tro bac si va gia dinh",
            "theo doi sinh hieu va quan ly ho so benh an",
            "tu van cham soc va phuc hoi cho nguoi benh",
        ],
        "goal": "lam dieu duong benh vien hoac y te cong dong.",
    },
    "Ngon ngu Anh": {
        "so": "Ngon ngu",
        "mons": ["Anh", "Van"],
        "skills": ["Giao tiep", "Lap luan", "Phan tich"],
        "moi": ["Linh hoat", "Truong hoc", "Van phong"],
        "kw": [
            "tieng anh giao tiep phien dich nghe noi doc viet",
            "IELTS bien dich tai lieu quoc te van phong",
            "lam viec da ngon ngu va moi truong global",
            "xay dung ky nang viet hoc thuat va thuyet trinh",
        ],
        "goal": "lam bien dich vien hoac giao vien tieng Anh.",
    },
    "Luat": {
        "so": "Phap ly",
        "mons": ["Van", "Toan", "Su"],
        "skills": ["Lap luan", "Phan tich", "Ban linh"],
        "moi": ["Van phong"],
        "kw": [
            "luat phap ly hop dong tranh tung phap che doanh nghiep",
            "nghien cuu van ban quy dinh bao ve quyen loi khach hang",
            "tu van phap luat va giai quyet tranh chap dan su",
            "lap luan logic va phan bien tren co so chung cu",
        ],
        "goal": "lam luat su hoac chuyen vien phap che.",
    },
    "Su pham": {
        "so": "Giao duc",
        "mons": ["Van", "Toan", "Anh", "Sinh"],
        "skills": ["Giao tiep", "Kien nhan", "Giai quyet van de"],
        "moi": ["Truong hoc"],
        "kw": [
            "su pham day hoc giao an tam ly hoc duong lop hoc",
            "huong dan hoc sinh phu dao ky nang mem giao tiep",
            "truyen cam hung hoc tap va danh gia tien bo",
            "xay dung moi truong lop hoc tich cuc",
        ],
        "goal": "day hoc pho thong hoac trung tam.",
    },
    "He thong thong tin quan ly": {
        "so": "Cong nghe",
        "mons": ["Tin hoc", "Toan", "Van"],
        "skills": ["Phan tich", "Giao tiep", "Giai quyet van de"],
        "moi": ["Van phong", "Ky thuat", "Linh hoat"],
        "kw": [
            "ERP he thong thong tin quan ly phan tich nghiep vu",
            "business analyst quy trinh doanh nghiep va CSDL",
            "tich hop phan mem quan tri du lieu noi bo",
            "ket hop IT va van hanh van phong tong hop",
        ],
        "goal": "lam BA chuyen gia ERP va quy trinh.",
    },
    "Ke toan tai chinh": {
        "so": "Kinh doanh",
        "mons": ["Toan", "Van"],
        "skills": ["Phan tich", "Can than", "Ky luat"],
        "moi": ["Van phong"],
        "kw": [
            "ke toan tai chinh bao cao thue bang can doi kiem toan",
            "so sach chi phi loi nhuan dinh muc ngan sach",
            "tu van ho so thue va quan tri rui ro tai chinh",
            "kiem soat dong tien va lap ke hoach ngan sach",
        ],
        "goal": "lam ke toan truong hoac kiem toan vien.",
    },
    "Du lich va lu hanh": {
        "so": "Kinh doanh",
        "mons": ["Anh", "Van"],
        "skills": ["Giao tiep", "Lanh dao", "Sang tao"],
        "moi": ["Linh hoat", "Van phong"],
        "kw": [
            "du lich lu hanh tour huong dan vien khach san",
            "dich vu khach hang van hoa dia phuong booking",
            "to chuc su kien travel agency quoc te",
            "tao trai nghiem hanh trinh an toan va dang nho",
        ],
        "goal": "dieu hanh tour va quan tri dich vu lu hanh.",
    },
    "Du lich": {
        "so": "Du lich",
        "mons": ["Anh", "Van", "Su"],
        "skills": ["Giao tiep", "Sang tao", "Lanh dao"],
        "moi": ["Linh hoat", "Sang tao"],
        "kw": [
            "du lich khac phuong thi truong diem den hap dan",
            "giao tiep khach hang va tao trai nghiem du lich",
            "tung hop am thuc van hoa dia phuong di san",
            "hao hang khach san va dich vu luu tru chat luong",
        ],
        "goal": "lam chuyen gia du lich hoac o quan ly dich vu.",
    },
    "Huong dan du lich": {
        "so": "Du lich",
        "mons": ["Anh", "Van"],
        "skills": ["Giao tiep", "Thuyet trinh", "Sang tao"],
        "moi": ["Linh hoat"],
        "kw": [
            "huong dan du lich ngoai ngu gioi thieu dia diem",
            "thuyet trinh van hoa lich su di san the gioi",
            "giao tiep da chung toc va khach hang quoc te",
            "lap lich trinh tour an toan va dang nho",
        ],
        "goal": "tro thanh huong dan du lich chuyen nghiep.",
    },
    "Quan tri dich vu du lich va lu hanh": {
        "so": "Du lich",
        "mons": ["Anh", "Van", "Toan"],
        "skills": ["Lanh dao", "Giao tiep", "Phan tich"],
        "moi": ["Van phong", "Linh hoat"],
        "kw": [
            "quan tri tour operation staff va dich vu khach hang",
            "lap kehoach campaign du lich co loi nhuan",
            "phan tich thi truong du lich va xu huong",
            "dieu phoi hotel flights va hoat dong du lich",
        ],
        "goal": "dieu hanh cong ty du lich hoac travel agency.",
    },
    "Bao chi va truyen thong": {
        "so": "Kinh doanh",
        "mons": ["Van", "Anh"],
        "skills": ["Giao tiep", "Sang tao", "Lap luan"],
        "moi": ["Van phong", "Sang tao", "Linh hoat"],
        "kw": [
            "bao chi phong van bien tap tin tuc truyen thong",
            "PR quan he cong chung media da phuong tien",
            "san xuat noi dung podcast video thoi su",
            "kiem chung thong tin va xay dung thong diep cong chung",
        ],
        "goal": "lam phong vien hoac truyen thong noi bo.",
    },
    "Kien truc": {
        "so": "Nghe thuat",
        "mons": ["Ly", "Van", "Toan"],
        "skills": ["Sang tao", "Phan tich", "Tu duy khong gian"],
        "moi": ["Sang tao", "Ky thuat", "Van phong"],
        "kw": [
            "kien truc thiet ke cong trinh quy hoach khong gian",
            "ket cau xay dung 3D mo hinh vat lieu xanh",
            "noi that cong cong anh sang tu nhien my thuat",
            "ve mat bang va y tuong kien truc ben vung",
        ],
        "goal": "lam kien truc su thiet ke cong trinh.",
    },
    "Ky thuat co khi": {
        "so": "Cong nghe",
        "mons": ["Ly", "Toan", "Tin hoc"],
        "skills": ["Giai quyet van de", "Phan tich", "Ky luat"],
        "moi": ["Ky thuat", "Van phong", "Linh hoat"],
        "kw": [
            "co khi ky thuat may moc CAD che tao tu dong hoa",
            "day chuyen san xuat robot cong nghiep nhiet dong hoc",
            "vat lieu ky thuat do luong va bao tri thiet bi",
            "van hanh xuong san xuat va toi uu quy trinh",
        ],
        "goal": "lam ky su co khi che tao va bao tri.",
    },
}

CONFUSION_PAIRS = {
    "Cong nghe thong tin": "He thong thong tin quan ly",
    "He thong thong tin quan ly": "Cong nghe thong tin",
    "Khoa hoc du lieu": "Cong nghe thong tin",
    "Marketing": "Bao chi va truyen thong",
    "Bao chi va truyen thong": "Marketing",
    "Quan tri kinh doanh": "Ke toan tai chinh",
    "Ke toan tai chinh": "Quan tri kinh doanh",
    "Thiet ke do hoa": "Kien truc",
    "Kien truc": "Thiet ke do hoa",
    "Du lich va lu hanh": "Ngon ngu Anh",
    "Ngon ngu Anh": "Du lich va lu hanh",
}

FIELD_POOLS = {
    "so_thich_chinh": sorted({v["so"] for v in PROFILE.values()}),
    "mon_hoc_yeu_thich": sorted({m for v in PROFILE.values() for m in v["mons"]}),
    "ky_nang_noi_bat": sorted({s for v in PROFILE.values() for s in v["skills"]}),
    "tinh_cach": TINH_OPTIONS,
    "moi_truong_lam_viec_mong_muon": sorted({m for v in PROFILE.values() for m in v["moi"]}),
    "muc_tieu_nghe_nghiep": MUC_OPTIONS,
}

TEXT_PREFIX = [
    "Em rat quan tam den",
    "Ban than em yeu thich",
    "Gan day em dau tu thoi gian cho",
    "Em thuong tim hieu them ve",
    "Em co xu huong tap trung vao",
]
TEXT_SUFFIX = [
    "va muon phat trien lau dai.",
    "de tao gia tri thuc te cho cong viec.",
    "vi em thay linh vuc nay phu hop tinh cach.",
    "nham nang cao co hoi nghe nghiep sau nay.",
    "de ket hop dam me voi nang luc cua minh.",
]
GOAL_PREFIX = [
    "Trong 3-5 nam toi, em muon",
    "Muc tieu nghe nghiep cua em la",
    "Em dinh huong se",
    "Duong dai em mong muon",
]
HOLDOUT_PREFIX = [
    "Neu noi ve dinh huong, em uu tien",
    "Khi tim nganh phu hop, em tap trung vao",
    "Tu trai nghiem hoc tap, em nhan ra minh hop voi",
]


def pick(seq: list[str], i: int) -> str:
    return seq[i % len(seq)]


def varied_text(core: str, idx: int, rng: random.Random, holdout: bool = False) -> str:
    if holdout:
        prefix = pick(HOLDOUT_PREFIX, idx + rng.randint(0, len(HOLDOUT_PREFIX) - 1))
    else:
        prefix = pick(TEXT_PREFIX, idx + rng.randint(0, len(TEXT_PREFIX) - 1))
    suffix = pick(TEXT_SUFFIX, idx + rng.randint(0, len(TEXT_SUFFIX) - 1))
    middle = core
    if rng.random() < 0.35:
        middle = middle.replace(" va ", " cung nhu ")
    if rng.random() < 0.25:
        middle = middle.replace("thich", "quan tam")
    return f"{prefix} {middle}, {suffix}"


def varied_goal(goal: str, idx: int, rng: random.Random) -> str:
    prefix = pick(GOAL_PREFIX, idx + rng.randint(0, len(GOAL_PREFIX) - 1))
    return f"{prefix} {goal}"


def inject_controlled_noise(row: dict[str, str], rng: random.Random) -> dict[str, str]:
    out = dict(row)
    if rng.random() >= NOISE_RATE:
        return out

    n_fields = 1 if rng.random() < 0.8 else 2
    fields = rng.sample(list(FIELD_POOLS.keys()), k=n_fields)
    for field in fields:
        candidates = [x for x in FIELD_POOLS[field] if x != out[field]]
        if candidates:
            out[field] = rng.choice(candidates)
    return out


def inject_hard_negative(row: dict[str, str], major: str, rng: random.Random) -> dict[str, str]:
    out = dict(row)
    if rng.random() >= HARD_NEGATIVE_RATE:
        return out

    confuse_major = CONFUSION_PAIRS.get(major)
    if not confuse_major:
        return out

    confuse = PROFILE[confuse_major]
    # Tron 1 phan thong tin cua nganh de nham nhat vao mau hien tai, nhung giu label goc
    out["mon_hoc_yeu_thich"] = rng.choice(confuse["mons"])
    out["ky_nang_noi_bat"] = rng.choice(confuse["skills"])
    if rng.random() < 0.5:
        out["moi_truong_lam_viec_mong_muon"] = rng.choice(confuse["moi"])
    out["mo_ta_ban_than"] = out["mo_ta_ban_than"] + f" Em cung quan tam den {rng.choice(confuse['kw'])}."
    return out


def row_for_major(major: str, idx: int, holdout: bool = False) -> tuple[str, ...]:
    salt = 7919 if holdout else 0
    rng = random.Random((hash(major) & 0xFFFF) * 1000 + idx + salt)
    
    # Use PROFILE if available, otherwise generate synthetic profile
    if major in PROFILE:
        p = PROFILE[major]
    else:
        # Generate synthetic profile for majors not in PROFILE
        p = {
            "so": rng.choice(["Cong nghe", "Kinh doanh", "Nghe thuat", "Y te", "Ngon ngu", "Giao duc", "Phap ly"]),
            "mons": rng.sample(["Toan", "Van", "Anh", "Tin hoc", "Sinh", "Hoa", "Ly", "Su"], k=2),
            "skills": rng.sample(["Phan tich", "Giao tiep", "Sang tao", "Lanh dao", "Can than", "Kien nhan", "Ky luat"], k=2),
            "moi": rng.sample(["Ky thuat", "Van phong", "Linh hoat", "Benh vien", "Truong hoc"], k=2),
            "kw": [f"Em thich lam viec voi {major}"] * 4,
            "goal": f"Em muon lam viec trong linh vuc {major}.",
        }

    row = {
        "so_thich_chinh": p["so"],
        "mon_hoc_yeu_thich": rng.choice(p["mons"]),
        "ky_nang_noi_bat": rng.choice(p["skills"]),
        "tinh_cach": TINH_OPTIONS[(idx + (hash(major) % 7)) % len(TINH_OPTIONS)],
        "moi_truong_lam_viec_mong_muon": rng.choice(p["moi"]),
        "muc_tieu_nghe_nghiep": MUC_OPTIONS[(idx * 3 + len(major)) % len(MUC_OPTIONS)],
        "mo_ta_ban_than": varied_text(rng.choice(p["kw"]), idx, rng, holdout=holdout),
        "dinh_huong_tuong_lai": varied_goal(p["goal"], idx, rng),
        "nganh_phu_hop": major,
    }

    if not holdout:
        row = inject_controlled_noise(row, rng)
        row = inject_hard_negative(row, major, rng)

    return (
        row["so_thich_chinh"],
        row["mon_hoc_yeu_thich"],
        row["ky_nang_noi_bat"],
        row["tinh_cach"],
        row["moi_truong_lam_viec_mong_muon"],
        row["muc_tieu_nghe_nghiep"],
        row["mo_ta_ban_than"],
        row["dinh_huong_tuong_lai"],
        row["nganh_phu_hop"],
    )


def write_csv(path: Path, rows: list[tuple[str, ...]]) -> None:
    header = [
        "so_thich_chinh",
        "mon_hoc_yeu_thich",
        "ky_nang_noi_bat",
        "tinh_cach",
        "moi_truong_lam_viec_mong_muon",
        "muc_tieu_nghe_nghiep",
        "mo_ta_ban_than",
        "dinh_huong_tuong_lai",
        "nganh_phu_hop",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(list(r))


def main() -> None:
    train_rows: list[tuple[str, ...]] = []
    holdout_rows: list[tuple[str, ...]] = []

    for major in MAJORS_ORDER:
        for i in range(ROWS_PER_MAJOR):
            train_rows.append(row_for_major(major, i, holdout=False))
        for i in range(HOLDOUT_ROWS_PER_MAJOR):
            holdout_rows.append(row_for_major(major, i, holdout=True))

    random.shuffle(train_rows)
    random.shuffle(holdout_rows)

    write_csv(OUT_TRAIN, train_rows)
    write_csv(OUT_HOLDOUT, holdout_rows)

    print(
        f"[OK] train: {len(train_rows)} dong ({ROWS_PER_MAJOR} x {len(MAJORS_ORDER)}), "
        f"noise={int(NOISE_RATE * 100)}%, hard_negative={int(HARD_NEGATIVE_RATE * 100)}% -> {OUT_TRAIN.relative_to(ROOT)}"
    )
    print(
        f"[OK] holdout: {len(holdout_rows)} dong ({HOLDOUT_ROWS_PER_MAJOR} x {len(MAJORS_ORDER)}) "
        f"-> {OUT_HOLDOUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
