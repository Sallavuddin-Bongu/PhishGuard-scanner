"""Loads the trained model and returns a calibrated phishing probability. No fallback predictions."""
from functools import lru_cache

import joblib
import pandas as pd

from app import config
from app.ml.features import FEATURE_NAMES, extract_features


class ModelNotFoundError(RuntimeError):
    pass


class ModelMismatchError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_bundle(path_str: str) -> dict:
    from pathlib import Path

    path = Path(path_str)
    if not path.exists():
        raise ModelNotFoundError(
            f"The ML model file was not found at {path}. "
            "Train it first: python -m app.ml.train --data <path-to-PhiUSIIL_Phishing_URL_Dataset.csv>"
        )
    bundle = joblib.load(path)
    if bundle.get("feature_names") != FEATURE_NAMES:
        raise ModelMismatchError(
            "The saved model was trained with different features than the current code. Retrain the model."
        )
    return bundle


def get_bundle() -> dict:
    # Read MODEL_PATH at call time so tests can point it elsewhere.
    return _load_bundle(str(config.MODEL_PATH))


def clear_model_cache():
    _load_bundle.cache_clear()


def predict_phishing_probability(normalized_url: str) -> float:
    bundle = get_bundle()
    frame = pd.DataFrame([extract_features(normalized_url)], columns=FEATURE_NAMES)
    raw = bundle["forest"].predict_proba(frame)[:, 1].reshape(-1, 1)
    calibrated = bundle["calibrator"].predict_proba(raw)[:, 1]
    return float(calibrated[0])
