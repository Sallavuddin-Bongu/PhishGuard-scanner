"""Exact-match lookup against the training dataset. Works only when DATASET_PATH is set."""
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app import config
from app.ml.normalize import InvalidURLError, normalize_url


@lru_cache(maxsize=1)
def _index() -> dict[str, int]:
    """Map normalized URL -> label (0 = phishing, 1 = legitimate, as in the PhiUSIIL file)."""
    if not config.DATASET_PATH:
        return {}
    path = Path(config.DATASET_PATH)
    if not path.exists():
        return {}
    df = pd.read_csv(path, usecols=["URL", "label"])
    index: dict[str, int] = {}
    labels = pd.to_numeric(df["label"], errors="coerce")
    for url, label in zip(df["URL"].astype(str), labels):
        if label not in (0, 1):
            continue
        try:
            index[normalize_url(url)] = int(label)
        except InvalidURLError:
            continue
    return index


def lookup(normalized_url: str) -> str | None:
    """Return 'phishing' or 'legitimate' if this exact URL is in the dataset, otherwise None."""
    label = _index().get(normalized_url)
    if label is None:
        return None
    return "legitimate" if label == 1 else "phishing"