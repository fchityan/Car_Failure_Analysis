from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

from .pipeline import (
    FEATURE_COLUMNS,
    evaluate_probabilities,
    fit_candidates,
    prepare_training_data,
    select_best_candidate,
    split_data,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a production-oriented vehicle failure classifier.")
    parser.add_argument("--data", default="Failure.csv", help="Path to the source Failure.csv file.")
    parser.add_argument("--artifacts-dir", default="artifacts", help="Directory for model artifacts.")
    parser.add_argument("--outputs-dir", default="outputs", help="Directory for evaluation outputs.")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.is_file():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    artifacts_dir = Path(args.artifacts_dir)
    outputs_dir = Path(args.outputs_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(data_path)
    X, y = prepare_training_data(raw)
    splits = split_data(X, y, random_state=args.random_state)

    candidates = fit_candidates(splits, random_state=args.random_state)
    best = select_best_candidate(candidates)

    validation_rows = []
    for candidate in candidates:
        metrics = candidate["metrics"]
        validation_rows.append(
            {
                "model": candidate["name"],
                "threshold": candidate["threshold"],
                "roc_auc": metrics["roc_auc"],
                "average_precision": metrics["average_precision"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "f2": metrics["f2"],
            }
        )
    pd.DataFrame(validation_rows).sort_values("average_precision", ascending=False).to_csv(
        outputs_dir / "validation_model_comparison.csv", index=False
    )
    best["threshold_table"].to_csv(outputs_dir / "threshold_tuning.csv", index=False)

    X_trainval = pd.concat([splits.X_train, splits.X_val], axis=0)
    y_trainval = pd.concat([splits.y_train, splits.y_val], axis=0)
    final_pipeline = best["pipeline"]
    final_pipeline.fit(X_trainval, y_trainval)

    test_probabilities = final_pipeline.predict_proba(splits.X_test)[:, 1]
    test_metrics = evaluate_probabilities(splits.y_test, test_probabilities, best["threshold"])

    created_at = datetime.now(timezone.utc).isoformat()
    model_version = f"{best['name']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    bundle = {
        "model": final_pipeline,
        "model_name": best["name"],
        "model_version": model_version,
        "created_at_utc": created_at,
        "threshold": float(best["threshold"]),
        "feature_columns": FEATURE_COLUMNS,
        "target_definition": "1 when any Failure A-E indicator equals 1; otherwise 0",
        "random_state": args.random_state,
    }
    model_path = artifacts_dir / "model_bundle.joblib"
    joblib.dump(bundle, model_path)

    summary = {
        "model_name": best["name"],
        "model_version": model_version,
        "threshold": float(best["threshold"]),
        "rows": int(len(X)),
        "failure_rate": float(y.mean()),
        "split_rows": {
            "train": int(len(splits.X_train)),
            "validation": int(len(splits.X_val)),
            "test": int(len(splits.X_test)),
        },
        "test_metrics": test_metrics,
        "artifact": str(model_path),
    }
    with (outputs_dir / "training_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    predictions = splits.X_test.copy()
    predictions["actual_failure"] = splits.y_test.to_numpy()
    predictions["failure_probability"] = test_probabilities
    predictions["predicted_failure"] = (test_probabilities >= best["threshold"]).astype(int)
    predictions.to_csv(outputs_dir / "test_predictions.csv", index=False)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
