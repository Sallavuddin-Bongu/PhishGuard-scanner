"""Train, calibrate, and evaluate the PhishGuard model.

Usage (from the backend folder):
    python -m app.ml.train --data path/to/PhiUSIIL_Phishing_URL_Dataset.csv

The CSV must have a URL column and a label column. The PhiUSIIL dataset uses
the column names "URL" and "label", with 0 = Phishing and 1 = Legitimate.
This script converts the labels to PhishGuard's convention: 0 = Legitimate, 1 = Phishing.

Outputs (in backend/model/):
    phishguard_model.joblib   the saved model bundle
    training_metrics.json     all metrics from this run
    training_report.md        a readable report
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit

from app.config import BASE_DIR, DECISION_THRESHOLD
from app.ml.features import FEATURE_NAMES, extract_features
from app.ml.normalize import InvalidURLError, normalize_url

MODEL_DIR = BASE_DIR / "model"
PHISHING = 1
LEGITIMATE = 0
ORIGINAL_PHISHING_LABEL = 0  # in PhiUSIIL: 0 = Phishing, 1 = Legitimate


def registered_domain(normalized_url: str) -> str:
    """Approximate registered domain (last two labels). Used only to group rows for splitting."""
    from urllib.parse import urlsplit

    host = urlsplit(normalized_url).hostname or ""
    labels = host.split(".")
    return ".".join(labels[-2:]) if len(labels) >= 2 else host


def load_and_clean(csv_path: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(csv_path)
    report = {"rows_loaded": int(len(raw)), "columns": list(raw.columns)}
    for needed in ("URL", "label"):
        if needed not in raw.columns:
            raise SystemExit(f"CSV is missing required column '{needed}'. Found: {list(raw.columns)}")

    df = raw[["URL", "label"]].copy()
    before = len(df)
    df = df.dropna(subset=["URL", "label"])
    report["rows_dropped_missing"] = before - len(df)

    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    before = len(df)
    df = df[df["label"].isin([0, 1])]
    report["rows_dropped_bad_label"] = before - len(df)

    urls, keep = [], []
    for i, u in enumerate(df["URL"].astype(str)):
        try:
            urls.append(normalize_url(u))
            keep.append(True)
        except InvalidURLError:
            urls.append("")
            keep.append(False)
    df["url_norm"] = urls
    report["rows_dropped_invalid_url"] = int((~np.array(keep)).sum())
    df = df[np.array(keep)]

    before = len(df)
    df = df.drop_duplicates(subset=["url_norm"])
    report["rows_dropped_duplicates"] = before - len(df)

    # Convert labels: original 0 = Phishing, 1 = Legitimate  ->  PhishGuard 1 = Phishing, 0 = Legitimate
    df["y"] = np.where(df["label"].astype(int) == ORIGINAL_PHISHING_LABEL, PHISHING, LEGITIMATE)
    report["rows_clean"] = int(len(df))
    report["clean_label_counts"] = {
        "phishing_1": int((df["y"] == PHISHING).sum()),
        "legitimate_0": int((df["y"] == LEGITIMATE).sum()),
    }
    if report["clean_label_counts"]["phishing_1"] == 0 or report["clean_label_counts"]["legitimate_0"] == 0:
        raise SystemExit("After cleaning, one class is empty. Check the label column.")
    return df.reset_index(drop=True), report


def build_matrix(urls: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([extract_features(u) for u in urls], columns=FEATURE_NAMES)


def compute_metrics(y_true: np.ndarray, prob: np.ndarray, threshold: float) -> dict:
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[LEGITIMATE, PHISHING]).ravel()
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision_phishing": float(precision_score(y_true, pred, zero_division=0)),
        "recall_phishing": float(recall_score(y_true, pred, zero_division=0)),
        "f1_phishing": float(f1_score(y_true, pred, zero_division=0)),
        "macro_f1": float(f1_score(y_true, pred, average="macro", zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) else 0.0,
        "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) else 0.0,
        "roc_auc": float(roc_auc_score(y_true, prob)),
        "pr_auc": float(average_precision_score(y_true, prob)),
        "brier_score": float(brier_score_loss(y_true, prob)),
    }


def main():
    parser = argparse.ArgumentParser(description="Train the PhishGuard URL model.")
    parser.add_argument("--data", required=True, type=Path, help="Path to the PhiUSIIL CSV file")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df, report = load_and_clean(args.data)
    print(f"Clean rows: {report['rows_clean']}  labels: {report['clean_label_counts']}")

    groups = df["url_norm"].map(registered_domain)

    # Split by domain group so the same domain never appears in two splits.
    outer = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=args.seed)
    train_val_idx, test_idx = next(outer.split(df, df["y"], groups))
    inner = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=args.seed)
    tv_groups = groups.iloc[train_val_idx]
    tr_rel, cal_rel = next(inner.split(df.iloc[train_val_idx], df["y"].iloc[train_val_idx], tv_groups))
    train_idx, cal_idx = train_val_idx[tr_rel], train_val_idx[cal_rel]

    assert not set(groups.iloc[train_idx]) & set(groups.iloc[test_idx]), "domain leak train/test"
    assert not set(groups.iloc[train_idx]) & set(groups.iloc[cal_idx]), "domain leak train/calibration"

    X = build_matrix(df["url_norm"])
    y = df["y"].to_numpy()
    X_train, y_train = X.iloc[train_idx], y[train_idx]
    X_cal, y_cal = X.iloc[cal_idx], y[cal_idx]
    X_test, y_test = X.iloc[test_idx], y[test_idx]
    print(f"Split sizes  train: {len(X_train)}  calibration: {len(X_cal)}  test: {len(X_test)}")

    # Limit tree depth and leaf size. Unlimited trees give almost every URL a raw probability of exactly 0 or 1,
    # which makes the calibrated score jump between only two values (for example 0 and 100).
    forest = RandomForestClassifier(
        n_estimators=200,
        max_depth=14,
        min_samples_leaf=25,
        max_features="sqrt",
        n_jobs=-1,
        random_state=args.seed,
        class_weight="balanced",
    )
    forest.fit(X_train, y_train)

    # Platt scaling on the calibration split only.
    cal_raw = forest.predict_proba(X_cal)[:, 1].reshape(-1, 1)
    calibrator = LogisticRegression()
    calibrator.fit(cal_raw, y_cal)

    def calibrated(frame: pd.DataFrame) -> np.ndarray:
        raw = forest.predict_proba(frame)[:, 1].reshape(-1, 1)
        return calibrator.predict_proba(raw)[:, 1]

    test_prob = calibrated(X_test)
    raw_test = forest.predict_proba(X_test)[:, 1]
    saturation = {
        "raw_forest_at_exact_0_or_1": float(np.mean((raw_test <= 0.0) | (raw_test >= 1.0))),
        "calibrated_below_0.01_or_above_0.99": float(np.mean((test_prob < 0.01) | (test_prob > 0.99))),
        "distinct_calibrated_values_in_test": int(len(np.unique(np.round(test_prob, 4)))),
    }
    metrics = compute_metrics(y_test, test_prob, DECISION_THRESHOLD)
    uncalibrated = compute_metrics(y_test, forest.predict_proba(X_test)[:, 1], DECISION_THRESHOLD)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "forest": forest,
        "calibrator": calibrator,
        "feature_names": FEATURE_NAMES,
        "threshold": DECISION_THRESHOLD,
        "label_map": {"0": "legitimate", "1": "phishing"},
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    joblib.dump(bundle, MODEL_DIR / "phishguard_model.joblib")

    result = {
        "data_file": str(args.data),
        "synthetic_demo_data": "synthetic" in args.data.name.lower(),
        "cleaning": report,
        "split_sizes": {"train": int(len(X_train)), "calibration": int(len(X_cal)), "test": int(len(X_test))},
        "features": FEATURE_NAMES,
        "test_metrics_calibrated": metrics,
        "test_metrics_uncalibrated": uncalibrated,
        "score_saturation_check": saturation,
    }
    print("Score saturation check:", json.dumps(saturation, indent=2))
    (MODEL_DIR / "training_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(MODEL_DIR / "training_report.md", result)

    print(json.dumps(metrics, indent=2))
    print(f"Saved model to {MODEL_DIR / 'phishguard_model.joblib'}")


def write_report(path: Path, r: dict):
    m = r["test_metrics_calibrated"]
    cm = m["confusion_matrix"]
    lines = [
        "# PhishGuard Training Report",
        "",
        f"Data file: `{r['data_file']}`",
        "",
        *(
            ["**DEMO MODEL: trained on SYNTHETIC generated URLs. These metrics do not describe real phishing detection.**", ""]
            if r.get("synthetic_demo_data") else []
        ),
        "## Limitation",
        "",
        "This model uses only features that can be computed from the URL text. The original PhiUSIIL dataset "
        "also has features from page HTML and JavaScript. Those are NOT used here, so results are not comparable "
        "to the dataset's published results.",
        "",
        "## Label mapping",
        "",
        "Original PhiUSIIL: 0 = Phishing, 1 = Legitimate. PhishGuard: 0 = Legitimate, 1 = Phishing.",
        "",
        "## Cleaning",
        "",
        *[f"- {k}: {v}" for k, v in r["cleaning"].items() if k != "columns"],
        "",
        "## Split sizes (domain-grouped)",
        "",
        *[f"- {k}: {v}" for k, v in r["split_sizes"].items()],
        "",
        "## Test metrics (calibrated, untouched test split)",
        "",
        f"- Threshold: {m['threshold']}",
        f"- Accuracy: {m['accuracy']:.4f}",
        f"- Precision (phishing): {m['precision_phishing']:.4f}",
        f"- Recall (phishing): {m['recall_phishing']:.4f}",
        f"- F1 (phishing): {m['f1_phishing']:.4f}",
        f"- Macro F1: {m['macro_f1']:.4f}",
        f"- Confusion matrix: TN={cm['tn']} FP={cm['fp']} FN={cm['fn']} TP={cm['tp']}",
        f"- False positive rate: {m['false_positive_rate']:.4f}",
        f"- False negative rate: {m['false_negative_rate']:.4f}",
        f"- ROC-AUC: {m['roc_auc']:.4f}",
        f"- PR-AUC: {m['pr_auc']:.4f}",
        f"- Brier score: {m['brier_score']:.4f}",
        "",
        "## Features",
        "",
        ", ".join(r["features"]),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
