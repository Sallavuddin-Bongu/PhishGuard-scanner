"""Measure the scanner's accuracy on labeled URLs from the PhiUSIIL CSV.

Usage (from the backend folder):
    python -m app.eval_scanner --data "C:\path\to\PhiUSIIL_Phishing_URL_Dataset.csv" --n 300

- Samples N/2 phishing and N/2 legitimate URLs from the CSV.
- Runs scan_url() as the website does, with the exact-match dataset lookup turned off.
- Prints accuracy, precision, recall and error rates, and saves every result to backend/model/eval_results.csv.
- The URLs come from the training file, so the results are optimistic.
"""
import argparse
from pathlib import Path

import pandas as pd

from app import dataset_lookup, scanner
from app.config import BASE_DIR


def load_labeled(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, usecols=["URL", "label"]).dropna()
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df[df["label"].isin([0, 1])].copy()
    df["truth"] = df["label"].map({0: "phishing", 1: "legitimate"})  # PhiUSIIL: 0 = phishing
    return df


def metrics(rows: list[dict], predicted_positive) -> dict:
    tp = fp = tn = fn = 0
    for r in rows:
        actual_phish = r["truth"] == "phishing"
        predicted_phish = predicted_positive(r["verdict"])
        if actual_phish and predicted_phish:
            tp += 1
        elif actual_phish and not predicted_phish:
            fn += 1
        elif not actual_phish and predicted_phish:
            fp += 1
        else:
            tn += 1
    total = tp + fp + tn + fn
    return {
        "total": total,
        "accuracy": (tp + tn) / total if total else 0,
        "precision": tp / (tp + fp) if (tp + fp) else 0,
        "recall": tp / (tp + fn) if (tp + fn) else 0,
        "false_positive_rate": fp / (fp + tn) if (fp + tn) else 0,
        "false_negative_rate": fn / (fn + tp) if (fn + tp) else 0,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def print_block(title: str, m: dict):
    print(f"\n{title}")
    print(f"  Total URLs:                                 {m['total']}")
    print(f"  Accuracy:                                   {m['accuracy'] * 100:.1f}%")
    print(f"  Phishing caught (recall):                   {m['recall'] * 100:.1f}%")
    print(f"  Precision (of flagged, how many were phishing): {m['precision'] * 100:.1f}%")
    print(f"  Normal sites flagged (false positive rate): {m['false_positive_rate'] * 100:.1f}%")
    print(f"  Phishing missed (false negative rate):      {m['false_negative_rate'] * 100:.1f}%")
    print(f"  Confusion: TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate the PhishGuard scanner on labeled URLs.")
    parser.add_argument("--data", required=True, type=Path, help="Path to the PhiUSIIL CSV")
    parser.add_argument("--n", type=int, default=300, help="Total URLs to test (half phishing, half legitimate)")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    df = load_labeled(args.data)
    half = args.n // 2
    phish = df[df["truth"] == "phishing"].sample(half, random_state=args.seed)
    legit = df[df["truth"] == "legitimate"].sample(half, random_state=args.seed)
    sample = pd.concat([phish, legit])

    # Turn off the exact-match dataset lookup so the test measures patterns, not memorized URLs.
    dataset_lookup.lookup = lambda _url: None

    rows = []
    for url, truth in zip(sample["URL"], sample["truth"]):
        try:
            result = scanner.scan_url(str(url))
            rows.append({"url": url, "truth": truth, "verdict": result["verdict"], "risk": result["risk_score"]})
        except Exception as e:  # keep going if one URL cannot be scanned
            rows.append({"url": url, "truth": truth, "verdict": "ERROR", "risk": None, "error": str(e)})

    scored = [r for r in rows if r["verdict"] != "ERROR"]
    errors = len(rows) - len(scored)

    strict = metrics(scored, lambda v: v == "PHISHING")
    loose = metrics(scored, lambda v: v in ("PHISHING", "SUSPICIOUS"))

    print(f"URLs tested: {len(rows)}  (could not scan: {errors})")
    print_block("STRICT: only PHISHING counts as phishing", strict)
    print_block("LOOSE: PHISHING or SUSPICIOUS counts as phishing", loose)

    out = BASE_DIR / "model" / "eval_results.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nEvery result was saved to: {out}")


if __name__ == "__main__":
    main()