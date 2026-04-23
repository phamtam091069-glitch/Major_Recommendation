"""Huan luyen mo hinh lai: chon mo hinh thong minh (RF/LR) + xac suat hieu chinh + hybrid voi cosine."""
from __future__ import annotations

import json
import pickle
import shutil
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.sparse import hstack
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from utils.constants import (
    BASE_DIR,
    CATEGORICAL_COLS,
    HYBRID_CONFIG_PATH,
    HYBRID_WEIGHT_COSINE,
    HYBRID_WEIGHT_RF,
    MAJORS_SOURCE_PATH,
    MODEL_CLASSES_PATH,
    MODEL_MAJORS_PATH,
    MODEL_OHE_PATH,
    MODEL_RF_PATH,
    MODEL_TFIDF_PATH,
    MODELS_DIR,
    RAW_DATA_PATH,
    REPORTS_DIR,
    TARGET_COL,
)
from utils.features import build_profile_text, row_dict_from_payload

HOLDOUT_PATH = BASE_DIR / "data" / "raw" / "students_holdout.csv"


def build_feature_matrix(df: pd.DataFrame, encoder: OneHotEncoder, tfidf: TfidfVectorizer):
    x_cat = df[CATEGORICAL_COLS].fillna("khong xac dinh")
    x_cat = x_cat.apply(lambda col: col.astype(str).str.strip().str.lower())
    x_text = tfidf.transform(df["profile_text"])
    x_cat_encoded = encoder.transform(x_cat)
    return hstack([x_cat_encoded, x_text])


def cross_validate_macro_f1(
    x,
    y: pd.Series,
    estimator: Any,
    n_splits: int = 3,
) -> tuple[float, float]:
    n_splits = max(2, min(n_splits, int(y.value_counts().min())))
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores: list[float] = []
    for train_idx, val_idx in skf.split(x, y):
        x_tr = x[train_idx]
        x_va = x[val_idx]
        y_tr = y.iloc[train_idx]
        y_va = y.iloc[val_idx]

        m = clone(estimator)
        m.fit(x_tr, y_tr)
        pred = m.predict(x_va)
        scores.append(float(f1_score(y_va, pred, average="macro", zero_division=0)))

    mean = sum(scores) / len(scores)
    var = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = var**0.5
    return mean, std


def _pick_tfidf_size(n_rows: int) -> int:
    # Giam tai cho tap nho, van du dac trung cho tap lon.
    return max(500, min(1200, n_rows * 3))


def _normalize_categorical_df(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for col in CATEGORICAL_COLS:
        normalized[col] = normalized[col].apply(lambda v: row_dict_from_payload({col: v}).get(col, "khong xac dinh"))
    return normalized


def _safe_top_k_accuracy(y_true: pd.Series, y_prob, classes, k: int = 3) -> float:
    classes_list = list(classes)
    class_to_idx = {cls: idx for idx, cls in enumerate(classes_list)}
    y_true_idx = []
    prob_rows = []
    for label, row in zip(y_true.astype(str), y_prob):
        if label not in class_to_idx:
            continue
        y_true_idx.append(class_to_idx[label])
        prob_rows.append(row)
    if not y_true_idx:
        return 0.0
    import numpy as np
    prob_arr = np.asarray(prob_rows)
    topk = np.argsort(prob_arr, axis=1)[:, -k:]
    hits = sum(1 for i, true_idx in enumerate(y_true_idx) if true_idx in topk[i])
    return float(hits / len(y_true_idx))


def _build_models(cv_cal: int) -> dict[str, CalibratedClassifierCV]:
    rf_base = RandomForestClassifier(
        n_estimators=220,
        max_depth=14,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )

    lr_base = LogisticRegression(
        max_iter=1800,
        solver="saga",
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )

    return {
        "CalibratedRandomForest": CalibratedClassifierCV(
            estimator=rf_base,
            method="sigmoid",
            cv=cv_cal,
            ensemble=True,
        ),
        "CalibratedLogisticRegression": CalibratedClassifierCV(
            estimator=lr_base,
            method="sigmoid",
            cv=cv_cal,
            ensemble=True,
        ),
    }


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MAJORS_SOURCE_PATH.exists():
        raise FileNotFoundError(f"Thieu {MAJORS_SOURCE_PATH}")

    if MAJORS_SOURCE_PATH.resolve() != MODEL_MAJORS_PATH.resolve():
        shutil.copy(MAJORS_SOURCE_PATH, MODEL_MAJORS_PATH)

    df = pd.read_csv(RAW_DATA_PATH)
    df = df.dropna(subset=[TARGET_COL]).copy()
    df = _normalize_categorical_df(df)

    class_count = int(df[TARGET_COL].astype(str).nunique())
    if class_count < 60:
        raise ValueError(
            f"Tap du lieu hien tai chi co {class_count} lop, chua du 60 lop de train. "
            "Hay cap nhat data/raw/students.csv truoc khi train lai."
        )

    df["profile_text"] = df.apply(lambda r: build_profile_text(r), axis=1)

    x_cat = df[CATEGORICAL_COLS].fillna("Khong xac dinh")
    y = df[TARGET_COL].astype(str)

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    x_cat_encoded = encoder.fit_transform(x_cat)

    tfidf_size = _pick_tfidf_size(len(df))
    tfidf = TfidfVectorizer(max_features=tfidf_size, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    x_text = tfidf.fit_transform(df["profile_text"])

    x = hstack([x_cat_encoded, x_text])

    min_class_count = int(y.value_counts().min())
    if min_class_count < 2:
        print(
            f"[WARN] Moi lop chi co {min_class_count} mau, khong the stratify split. "
            "Se split ngau nhien de tranh loi train_test_split."
        )
        stratify_target = None
    else:
        stratify_target = y

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=stratify_target
    )

    n_splits_train = int(y_train.value_counts().min())
    cv_cal = max(2, min(3, n_splits_train))
    candidate_models = _build_models(cv_cal)

    eval_rows: list[dict[str, float | str]] = []
    best_name = ""
    best_model: CalibratedClassifierCV | None = None
    best_macro = -1.0
    best_top3 = -1.0

    for name, candidate in candidate_models.items():
        candidate.fit(x_train, y_train)
        pred = candidate.predict(x_test)
        prob = candidate.predict_proba(x_test)
        macro = f1_score(y_test, pred, average="macro", zero_division=0)
        acc = accuracy_score(y_test, pred)
        top3 = _safe_top_k_accuracy(y_test, prob, candidate.classes_, k=min(3, len(candidate.classes_)))

        eval_rows.append(
            {
                "model": name,
                "accuracy": float(acc),
                "macro_f1": float(macro),
                "top3": float(top3),
            }
        )

        if (macro > best_macro) or (abs(macro - best_macro) < 1e-9 and top3 > best_top3):
            best_name = name
            best_model = candidate
            best_macro = float(macro)
            best_top3 = float(top3)

    if best_model is None:
        raise RuntimeError("Khong the huan luyen duoc mo hinh nao.")

    model = best_model

    # CV gon hon de giam thoi gian train, van bao dam do on dinh.
    min_total_class = int(y.value_counts().min())
    n_splits_cv = max(2, min(3, min_total_class))
    cv_macro_mean, cv_macro_std = cross_validate_macro_f1(x, y, model, n_splits=n_splits_cv)

    y_pred = model.predict(x_test)
    y_prob = model.predict_proba(x_test)

    accuracy = accuracy_score(y_test, y_pred)
    k_top = min(3, len(model.classes_))
    top3 = _safe_top_k_accuracy(y_test, y_prob, model.classes_, k=k_top)
    report = classification_report(y_test, y_pred, zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    labels = list(model.classes_)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    pd.DataFrame(cm, index=labels, columns=labels).to_csv(
        REPORTS_DIR / "confusion_matrix.csv", encoding="utf-8-sig"
    )

    per_cls = precision_recall_fscore_support(y_test, y_pred, labels=labels, zero_division=0)
    per_class_rows = []
    for idx, label in enumerate(labels):
        per_class_rows.append(
            {
                "label": label,
                "precision": float(per_cls[0][idx]),
                "recall": float(per_cls[1][idx]),
                "f1": float(per_cls[2][idx]),
                "support": int(per_cls[3][idx]),
            }
        )
    pd.DataFrame(per_class_rows).to_csv(REPORTS_DIR / "per_class_metrics.csv", index=False, encoding="utf-8-sig")

    holdout_text = "Holdout dataset khong ton tai (bo qua)."
    if HOLDOUT_PATH.exists():
        holdout_df = pd.read_csv(HOLDOUT_PATH).dropna(subset=[TARGET_COL]).copy()
        holdout_df["profile_text"] = holdout_df.apply(lambda r: build_profile_text(r), axis=1)
        x_holdout = build_feature_matrix(holdout_df, encoder, tfidf)
        y_holdout = holdout_df[TARGET_COL].astype(str)
        pred_holdout = model.predict(x_holdout)
        prob_holdout = model.predict_proba(x_holdout)
        holdout_acc = accuracy_score(y_holdout, pred_holdout)
        holdout_macro_f1 = f1_score(y_holdout, pred_holdout, average="macro", zero_division=0)
        holdout_k = min(3, len(model.classes_))
        holdout_top3 = _safe_top_k_accuracy(
            y_holdout,
            prob_holdout,
            model.classes_,
            k=holdout_k,
        )
        holdout_text = (
            "=== HOLDOUT (template khac, khong train) ===\n"
            f"Path: {Path(HOLDOUT_PATH).relative_to(BASE_DIR)}\n"
            f"Rows: {len(holdout_df)}\n"
            f"Accuracy: {holdout_acc:.4f}\n"
            f"Top-3 Accuracy: {holdout_top3:.4f}\n"
            f"Macro-F1: {holdout_macro_f1:.4f}\n"
        )

    dt = DecisionTreeClassifier(max_depth=12, min_samples_leaf=2, class_weight="balanced", random_state=42)
    dt.fit(x_train, y_train)
    acc_dt = accuracy_score(y_test, dt.predict(x_test))

    lr_plain = LogisticRegression(
        max_iter=1800,
        solver="saga",
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
    )
    lr_plain.fit(x_train, y_train)
    acc_lr = accuracy_score(y_test, lr_plain.predict(x_test))

    joblib.dump(model, MODEL_RF_PATH)
    joblib.dump(encoder, MODEL_OHE_PATH)
    # Save tfidf with pickle (protocol 5) for better sparse matrix support
    with open(MODEL_TFIDF_PATH, "wb") as f:
        pickle.dump(tfidf, f, protocol=pickle.HIGHEST_PROTOCOL)
    joblib.dump(list(model.classes_), MODEL_CLASSES_PATH)

    hybrid_cfg = {
        "weight_rf": HYBRID_WEIGHT_RF,
        "weight_cosine": HYBRID_WEIGHT_COSINE,
        "model": best_name,
        "profile_text": "categorical_plus_essay",
        "majors_source": str(MAJORS_SOURCE_PATH.name),
        "tfidf_max_features": tfidf_size,
    }
    HYBRID_CONFIG_PATH.write_text(json.dumps(hybrid_cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    model_board = "\n".join(
        [
            f"- {row['model']}: acc={row['accuracy']:.4f}, macro_f1={row['macro_f1']:.4f}, top3={row['top3']:.4f}"
            for row in eval_rows
        ]
    )

    comparison = (
        "\n=== SO SANH THUAT TOAN (tap kiem tra 20%) ===\n"
        f"{model_board}\n"
        f"Decision Tree: {acc_dt:.4f}\n"
        f"Logistic Regression (plain): {acc_lr:.4f}\n"
        f"=> Chon mo hinh chinh: {best_name}\n"
    )

    evaluation_text = (
        "=== DANH GIA MO HINH CHINH (calibrated + hybrid) ===\n"
        f"Model: {best_name}\n"
        f"Accuracy: {accuracy:.4f}\n"
        f"Top-{k_top} Accuracy: {top3:.4f}\n"
        f"Macro-F1: {macro_f1:.4f}\n"
        f"Weighted-F1: {weighted_f1:.4f}\n"
        f"CV Macro-F1 ({n_splits_cv}-fold): {cv_macro_mean:.4f} ± {cv_macro_std:.4f}\n"
        f"TF-IDF max_features: {tfidf_size}\n\n"
        "=== BAO CAO PHAN LOP ===\n"
        f"{report}\n"
        f"{comparison}\n"
        f"{holdout_text}\n"
        "=== CONG THUC LAI KHI DU DOAN ===\n"
        f"{int(HYBRID_WEIGHT_RF * 100)}% xac suat model + "
        f"{int(HYBRID_WEIGHT_COSINE * 100)}% cosine (TF-IDF ho so vs ho so nganh)\n"
        "\n=== FILE BAO CAO BO SUNG ===\n"
        "- reports/confusion_matrix.csv\n"
        "- reports/per_class_metrics.csv\n"
    )
    (REPORTS_DIR / "evaluation.txt").write_text(evaluation_text, encoding="utf-8")

    report_path = REPORTS_DIR / "evaluation.txt"
    print(f"[OK] Da train xong. Bao cao da luu tai: {report_path}")
    print("[OK] Da train va dong bo vao models/ (gom hybrid_config.json, majors.json)")


if __name__ == "__main__":
    main()
