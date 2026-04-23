"""Ghep dac trung van ban ho so hoc sinh (dong bo train / du doan)."""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Mapping

import pandas as pd

from .constants import CATEGORICAL_COLS, TEXT_COLS


PUNCT_RE = re.compile(r"[^\w\s]+", flags=re.UNICODE)


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("&", " va ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = PUNCT_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _cell(row: Mapping[str, Any], col: str) -> str:
    if isinstance(row, Mapping) and not isinstance(row, pd.Series):
        raw = row.get(col, "")
    else:
        raw = row[col] if col in row.index else ""  # type: ignore[index]
    return str(raw).strip()


def build_profile_text(row: Mapping[str, Any]) -> str:
    """Noi dung ho so: cac truong chon + mo ta tu do."""
    parts: list[str] = []

    for col in CATEGORICAL_COLS:
        v = _normalize_text(_cell(row, col))
        if v and v.lower() != "nan":
            parts.append(v)

    essay = _normalize_text(" ".join(_cell(row, c) for c in TEXT_COLS))

    merged = " ".join(parts + ([essay] if essay else [])).strip()
    return merged


def row_dict_from_payload(payload: Mapping[str, str]) -> Dict[str, str]:
    """Chuan hoa payload API thanh dict day du cot."""
    out: dict[str, str] = {}
    for col in CATEGORICAL_COLS:
        v = _normalize_text(payload.get(col, ""))
        out[col] = v if v else "khong xac dinh"
    for col in TEXT_COLS:
        out[col] = _normalize_text(payload.get(col, ""))
    return out
