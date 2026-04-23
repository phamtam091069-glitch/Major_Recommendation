"""
Audit chat luong du lieu students.csv de tim loi nhan, mat can bang, missing, duplicate, outlier.
Chay:
    python data/audit_dataset.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "students.csv"
REPORTS_DIR = ROOT / "reports"
TXT_REPORT_PATH = REPORTS_DIR / "data_audit.txt"
JSON_REPORT_PATH = REPORTS_DIR / "data_audit.json"

TARGET_COL = "nganh_phu_hop"
CATEGORICAL_COLS = [
    "so_thich_chinh",
    "mon_hoc_yeu_thich",
    "ky_nang_noi_bat",
    "tinh_cach",
    "moi_truong_lam_viec_mong_muon",
    "muc_tieu_nghe_nghiep",
]
TEXT_COLS = ["mo_ta_ban_than", "dinh_huong_tuong_lai"]
EMPTY_LIKE = {"", " ", "na", "n/a", "none", "null", "nan", "khong xac dinh"}


@dataclass
class IQRStat:
    q1: float
    q3: float
    iqr: float
    lower: float
    upper: float


def _normalize_str(v: Any) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip().lower()


def _missing_and_empty_summary(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for col in df.columns:
        na_count = int(df[col].isna().sum())
        empty_like_count = int(df[col].map(_normalize_str).isin(EMPTY_LIKE).sum())
        out[col] = {
            "missing_na": na_count,
            "empty_like": empty_like_count,
        }
    return out


def _class_distribution(y: pd.Series) -> dict[str, Any]:
    counts = y.value_counts(dropna=False)
    total = int(counts.sum())
    detail = [
        {
            "label": str(label),
            "count": int(count),
            "ratio": float(count / total) if total else 0.0,
        }
        for label, count in counts.items()
    ]

    min_count = int(counts.min()) if len(counts) else 0
    max_count = int(counts.max()) if len(counts) else 0
    imbalance_ratio = float(max_count / min_count) if min_count > 0 else float("inf")

    return {
        "n_classes": int(len(counts)),
        "min_count": min_count,
        "max_count": max_count,
        "imbalance_ratio": imbalance_ratio,
        "distribution": detail,
    }


def _low_frequency_categories(df: pd.DataFrame, min_count: int = 3) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue
        vc = df[col].fillna("<NA>").astype(str).str.strip().value_counts()
        rare = vc[vc < min_count]
        out[col] = [{"value": k, "count": int(v)} for k, v in rare.items()]
    return out


def _text_length_stats(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for col in TEXT_COLS:
        if col not in df.columns:
            continue
        lengths = df[col].fillna("").astype(str).str.split().map(len)
        out[col] = {
            "min_words": int(lengths.min()) if len(lengths) else 0,
            "median_words": float(lengths.median()) if len(lengths) else 0.0,
            "max_words": int(lengths.max()) if len(lengths) else 0,
            "too_short_le_3_words": int((lengths <= 3).sum()),
        }
    return out


def _numeric_outliers(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        stat = IQRStat(q1=q1, q3=q3, iqr=iqr, lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr)
        outlier_mask = (df[col] < stat.lower) | (df[col] > stat.upper)
        out[col] = {
            "q1": stat.q1,
            "q3": stat.q3,
            "iqr": stat.iqr,
            "lower_bound": stat.lower,
            "upper_bound": stat.upper,
            "outlier_count": int(outlier_mask.sum()),
        }
    return out


def _exact_duplicate_rows(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def _build_recommendations(audit: dict[str, Any]) -> list[str]:
    recs: list[str] = []

    imbalance_ratio = audit["class_distribution"]["imbalance_ratio"]
    if imbalance_ratio > 1.5:
        recs.append(
            "Dataset dang mat can bang lop. Nen dung class_weight='balanced', hoac bo sung mau cho lop it mau."
        )

    target_missing = audit["missing_and_empty"].get(TARGET_COL, {})
    if target_missing.get("missing_na", 0) > 0 or target_missing.get("empty_like", 0) > 0:
        recs.append("Cot nhan nganh_phu_hop co gia tri thieu/rong. Can bo sung hoac loai bo dong loi.")

    if audit["duplicate_rows"] > 0:
        recs.append("Co dong du lieu trung lap hoan toan. Nen xoa duplicate truoc khi train.")

    short_a = audit["text_length"].get("mo_ta_ban_than", {}).get("too_short_le_3_words", 0)
    short_b = audit["text_length"].get("dinh_huong_tuong_lai", {}).get("too_short_le_3_words", 0)
    if short_a > 0 or short_b > 0:
        recs.append("Co nhieu mau text qua ngan (<= 3 tu). Nen bo sung noi dung de TF-IDF hoc tot hon.")

    for col, rares in audit["low_frequency_categories"].items():
        if rares:
            recs.append(f"Cot {col} co nhieu nhom hiem (<3 mau). Co the gom nhom hoac bo sung du lieu.")

    if not recs:
        recs.append("Khong phat hien van de nghiem trong. Nen tiep tuc theo doi metric macro-F1 sau moi lan cap nhat du lieu.")

    return recs


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Khong tim thay file du lieu: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    audit: dict[str, Any] = {
        "dataset_path": str(DATA_PATH.relative_to(ROOT)),
        "n_rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "missing_and_empty": _missing_and_empty_summary(df),
        "duplicate_rows": _exact_duplicate_rows(df),
        "class_distribution": _class_distribution(df[TARGET_COL].astype(str)),
        "low_frequency_categories": _low_frequency_categories(df),
        "text_length": _text_length_stats(df),
        "numeric_outliers": _numeric_outliers(df),
    }
    audit["recommendations"] = _build_recommendations(audit)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("=== DATA QUALITY AUDIT ===")
    lines.append(f"Dataset: {audit['dataset_path']}")
    lines.append(f"Rows: {audit['n_rows']} | Cols: {audit['n_columns']}")
    lines.append("")

    cls = audit["class_distribution"]
    lines.append("[1] Class distribution")
    lines.append(
        f"So lop: {cls['n_classes']} | min={cls['min_count']} | max={cls['max_count']} | imbalance_ratio={cls['imbalance_ratio']:.2f}"
    )
    for it in cls["distribution"]:
        lines.append(f"  - {it['label']}: {it['count']} ({it['ratio']:.2%})")
    lines.append("")

    lines.append("[2] Missing / empty-like theo cot")
    for col, s in audit["missing_and_empty"].items():
        lines.append(f"  - {col}: missing_na={s['missing_na']}, empty_like={s['empty_like']}")
    lines.append("")

    lines.append(f"[3] Duplicate rows: {audit['duplicate_rows']}")
    lines.append("")

    lines.append("[4] Text length stats")
    for col, s in audit["text_length"].items():
        lines.append(
            f"  - {col}: min={s['min_words']}, median={s['median_words']:.1f}, max={s['max_words']}, too_short(<=3)={s['too_short_le_3_words']}"
        )
    lines.append("")

    lines.append("[5] Low-frequency categories (<3 mau)")
    has_rare = False
    for col, rares in audit["low_frequency_categories"].items():
        if rares:
            has_rare = True
            joined = ", ".join([f"{r['value']}={r['count']}" for r in rares])
            lines.append(f"  - {col}: {joined}")
    if not has_rare:
        lines.append("  - Khong co")
    lines.append("")

    lines.append("[6] Numeric outlier (IQR)")
    if audit["numeric_outliers"]:
        for col, s in audit["numeric_outliers"].items():
            lines.append(
                f"  - {col}: outliers={s['outlier_count']}, bounds=[{s['lower_bound']:.3f}, {s['upper_bound']:.3f}]"
            )
    else:
        lines.append("  - Khong co cot numeric de kiem tra")
    lines.append("")

    lines.append("[7] Recommendations")
    for rec in audit["recommendations"]:
        lines.append(f"  - {rec}")

    text_report = "\n".join(lines) + "\n"
    TXT_REPORT_PATH.write_text(text_report, encoding="utf-8")

    print(text_report)
    print(f"[OK] JSON report: {JSON_REPORT_PATH.relative_to(ROOT)}")
    print(f"[OK] TXT report:  {TXT_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
