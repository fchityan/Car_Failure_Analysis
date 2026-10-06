"""Reusable training and evaluation utilities for predictive maintenance classification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "failure_target"
FAILURE_COLUMNS = ["failure_a", "failure_b", "failure_c", "failure_d", "failure_e"]
FEATURE_COLUMNS = [
    "model",
    "color",
    "temperature",
    "rpm",
    "factory",
    "usage",
    "fuel_consumption",
    "membership",
]
CATEGORICAL_COLUMNS = ["model", "color", "factory", "usage", "membership"]
NUMERIC_COLUMNS = ["temperature", "rpm", "fuel_consumption"]

COLUMN_ALIASES = {
    "Car ID": "car_id",
    "Model": "model",
    "Color": "color",
    "Temperature": "temperature",
    "RPM": "rpm",
    "Factory": "factory",
    "Usage": "usage",
    "Fuel consumption": "fuel_consumption",
    "Membership": "membership",
    "Failure A": "failure_a",
    "Failure B": "failure_b",
    "Failure C": "failure_c",
    "Failure D": "failure_d",
    "Failure E": "failure_e",
}


@dataclass
class DatasetSplits:
    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series


def normalize_schema(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize notebook-era column names to the production schema."""
    frame = dataframe.rename(columns=COLUMN_ALIASES).copy()
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    return frame


def prepare_training_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Clean source records and create the Fail/Pass classification target."""
    frame = normalize_schema(dataframe)
    missing_failures = [column for column in FAILURE_COLUMNS if column not in frame.columns]
    if missing_failures:
        raise ValueError(f"Missing failure indicator columns: {missing_failures}")

    missing_features = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing_features:
        raise ValueError(f"Missing model feature columns: {missing_features}")

    for column in FAILURE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0).astype(int)

    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame.loc[frame[column] <= 0, column] = np.nan

    for column in CATEGORICAL_COLUMNS:
        frame[column] = frame[column].astype("string").replace({"<NA>": pd.NA, "None": pd.NA})

    target = (frame[FAILURE_COLUMNS].eq(1).any(axis=1)).astype(int).rename(TARGET_COLUMN)
    features = frame[FEATURE_COLUMNS].copy()
    return features, target


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
) -> DatasetSplits:
    """Create stratified 60/20/20 train/validation/test splits."""
    if y.nunique() < 2:
        raise ValueError("Target must contain both failure and pass classes.")

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.40,
        random_state=random_state,
        stratify=y,
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=random_state,
        stratify=y_temp,
    )
    return DatasetSplits(X_train, X_val, X_test, y_train, y_val, y_test)


def build_preprocessor() -> ColumnTransformer:
    """Build one preprocessing contract shared by training and serving."""
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
        ],
        sparse_threshold=0.0,
    )


def candidate_models(random_state: int = 42) -> dict[str, Any]:
    return {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=random_state),
    }


def evaluate_probabilities(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "f2": float(fbeta_score(y_true, predictions, beta=2, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, predictions, labels=[0, 1]).tolist(),
        "threshold": float(threshold),
    }


def tune_threshold(y_true: pd.Series, probabilities: np.ndarray) -> tuple[float, pd.DataFrame]:
    """Choose a validation-only threshold that weights missed failures more heavily."""
    rows = []
    for threshold in np.arange(0.10, 0.91, 0.02):
        metrics = evaluate_probabilities(y_true, probabilities, float(threshold))
        rows.append({key: metrics[key] for key in ["threshold", "precision", "recall", "f1", "f2"]})
    results = pd.DataFrame(rows).sort_values(["f2", "recall"], ascending=False).reset_index(drop=True)
    return float(results.iloc[0]["threshold"]), results


def fit_candidates(splits: DatasetSplits, random_state: int = 42) -> list[dict[str, Any]]:
    """Fit candidate pipelines and evaluate each on the validation split."""
    results: list[dict[str, Any]] = []
    for name, classifier in candidate_models(random_state).items():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("classifier", classifier)])
        pipeline.fit(splits.X_train, splits.y_train)
        probabilities = pipeline.predict_proba(splits.X_val)[:, 1]
        threshold, threshold_table = tune_threshold(splits.y_val, probabilities)
        metrics = evaluate_probabilities(splits.y_val, probabilities, threshold)
        results.append(
            {
                "name": name,
                "pipeline": pipeline,
                "threshold": threshold,
                "threshold_table": threshold_table,
                "metrics": metrics,
            }
        )
    return results


def select_best_candidate(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Select by average precision, then recall-weighted F2 as tie-break."""
    if not results:
        raise ValueError("No candidate results supplied.")
    return sorted(
        results,
        key=lambda result: (result["metrics"]["average_precision"], result["metrics"]["f2"]),
        reverse=True,
    )[0]
