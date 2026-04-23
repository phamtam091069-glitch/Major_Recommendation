"""Ghep dac trung van ban ho so hoc sinh (dong bo train / du doan)."""
from __future__ import annotations

import re
from typing import Any, Mapping

import pandas as pd

from .constants import CATEGORICAL_COLS, TEXT_COLS


PUNCT_RE = re.compile(r"[^\w\s]+", flags=re.UNICODE)


def _cell(row: Mapping[str, Any] | pd.Series, col: str) -> str:
    if isinstance(row, Mapping) and not isinstance(row, pd.Series):
        raw = row.get(col, "")
    else:
        raw = row[col] if col in row.index else ""  # type: ignore[index]
    return str(raw).strip()


def build_profile_text(row: Mapping[str, Any] | pd.Series) -> str:
    """Noi dung ho so: cac truong chon + mo ta tu do."""
    parts: list[str] = []

    for col in CATEGORICAL_COLS:
        v = _cell(row, col)
        if v and v.lower() != "nan":
            parts.append(v.lower())

    essay = " ".join(_cell(row, c) for c in TEXT_COLS).lower()
    essay = PUNCT_RE.sub(" ", essay)
    essay = re.sub(r"\s+", " ", essay).strip()

    merged = " ".join(parts + [essay]).strip()
    return merged


def row_dict_from_payload(payload: Mapping[str, str]) -> dict[str, str]:
    """Chuan hoa payload API thanh dict day du cot."""
    out: dict[str, str] = {}
    for col in CATEGORICAL_COLS:
        v = str(payload.get(col, "") or "").strip()
        out[col] = v if v else "Khong xac dinh"
    for col in TEXT_COLS:
        out[col] = str(payload.get(col, "") or "").strip()
    return out
