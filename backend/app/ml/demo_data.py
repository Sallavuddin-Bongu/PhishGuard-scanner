"""Generates a SYNTHETIC demo dataset of URLs, for running the app without the real PhiUSIIL file.

WARNING: this data is made up. A model trained on it is only a demo. Its accuracy says nothing about
real phishing sites. Use the real PhiUSIIL dataset for any real evaluation.

Output uses the same convention as PhiUSIIL: label 0 = Phishing, 1 = Legitimate.
Usage: python -m app.ml.demo_data --out model/DEMO_synthetic_urls.csv
"""
import argparse
import csv
import random
from pathlib import Path

LEGIT_WORDS = ["shop", "news", "garden", "travel", "music", "school", "cloud", "health", "sports", "books",
               "coffee", "photo", "market", "weather", "docs", "science", "design", "recipes", "games", "bank"]
LEGIT_TLDS = ["com", "org", "net", "edu", "in", "co.uk", "io"]
BRANDS = ["paypal", "amazon", "netflix", "apple", "microsoft", "dropbox", "instagram", "sbi", "icici", "hdfc"]
PHISH_WORDS = ["secure", "verify", "login", "account", "update", "confirm", "signin", "billing", "unlock", "support"]
PHISH_TLDS = ["xyz", "top", "tk", "ml", "ga", "cf", "click", "info"]
PATHS = ["/", "/about", "/products/item{n}", "/blog/2024/post-{n}", "/index.html", "/contact"]


def legit_url(rng: random.Random) -> str:
    name = f"{rng.choice(LEGIT_WORDS)}{rng.choice(['', rng.choice(LEGIT_WORDS)])}"
    if rng.random() < 0.2:
        name = f"{rng.choice(LEGIT_WORDS)}-{rng.choice(LEGIT_WORDS)}"
    host = f"{name}.{rng.choice(LEGIT_TLDS)}"
    if rng.random() < 0.3:
        host = f"www.{host}"
    scheme = "https" if rng.random() < 0.8 else "http"
    path = rng.choice(PATHS).format(n=rng.randint(1, 999))
    query = f"?page={rng.randint(1, 50)}" if rng.random() < 0.2 else ""
    return f"{scheme}://{host}{path}{query}"


def phishing_url(rng: random.Random) -> str:
    roll = rng.random()
    if roll < 0.15:
        host = f"{rng.randint(10, 230)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    else:
        host = f"{rng.choice(BRANDS)}-{rng.choice(PHISH_WORDS)}-{rng.choice(PHISH_WORDS)}.{rng.choice(PHISH_TLDS)}"
        if rng.random() < 0.4:
            host = f"{rng.choice(PHISH_WORDS)}.{rng.choice(BRANDS)}.{rng.choice(PHISH_TLDS)}.{rng.choice(LEGIT_WORDS)}{rng.randint(1, 99)}.com"
    scheme = "http" if rng.random() < 0.4 else "https"
    path = f"/{rng.choice(PHISH_WORDS)}/{rng.choice(BRANDS)}/{rng.randint(10000, 99999)}"
    if rng.random() < 0.5:
        path += "?session=%2Fverify%2Faccount%3Fid%3D" + "%41" * rng.randint(2, 12)
    return f"{scheme}://{host}{path}"


def make_rows(n_each: int, seed: int, label_noise: float = 0.12):
    rng = random.Random(seed)
    rows = []
    for _ in range(n_each):
        # label 0 = Phishing, 1 = Legitimate (PhiUSIIL convention)
        rows.append((phishing_url(rng), 0))
        rows.append((legit_url(rng), 1))
    # Flip some labels so the task is not trivially easy.
    flipped = []
    for url, label in rows:
        if rng.random() < label_noise:
            label = 1 - label
        flipped.append((url, label))
    rng.shuffle(flipped)
    return flipped


def main():
    parser = argparse.ArgumentParser(description="Generate a SYNTHETIC demo URL dataset.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=8000, help="URLs per class")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    rows = make_rows(args.n, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["URL", "label"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} SYNTHETIC rows to {args.out}")


if __name__ == "__main__":
    main()
