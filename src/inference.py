from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import joblib
import numpy as np
import pandas as pd

from .pipeline import FEATURE_COLUMNS


def load_model_bundle(path: str | Path) -> dict[str, Any]:
    bundle = joblib.load(Path(path))
    required = {"model", "model_name", "model_version", "threshold", "feature_columns"}
    missing = required - set(bundle)
    if missing:
        raise ValueError(f"Model bundle is missing keys: {sorted(missing)}")
    return bundle


def prepare_records(records: Sequence[dict[str, Any]], feature_columns: Sequence[str] = FEATURE_COLUMNS) -> pd.DataFrame:
    if not records:
        raise ValueError("At least one record is required.")
    frame = pd.DataFrame(records)
    missing = [column for column in feature_columns if column not in frame.columns]
    unexpected = sorted(set(frame.columns) - set(feature_columns))
    if missing or unexpected:
        raise ValueError(f"Schema mismatch. missing={missing}, unexpected={unexpected}")

    for column in ["temperature", "rpm", "fuel_consumption"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any() or (~np.isfinite(frame[column])).any():
            raise ValueError(f"Column '{column}' must contain finite numeric values.")
        if (frame[column] <= 0).any():
            raise ValueError(f"Column '{column}' must be greater than zero.")
    return frame[list(feature_columns)].copy()


def predict_records(records: Sequence[dict[str, Any]], bundle: dict[str, Any]) -> list[dict[str, Any]]:
    frame = prepare_records(records, bundle["feature_columns"])
    probabilities = bundle["model"].predict_proba(frame)[:, 1]
    threshold = float(bundle["threshold"])
    return [
        {
            "failure_probability": float(probability),
            "predicted_failure": int(probability >= threshold),
            "threshold": threshold,
            "model_name": bundle["model_name"],
            "model_version": bundle["model_version"],
        }
        for probability in probabilities
    ]
