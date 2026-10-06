# Vehicle Failure Risk — Production ML

A production-oriented predictive-maintenance classification project built from the original Car Failure exploratory analysis.

The original notebook, `car_failure_analysis.ipynb`, is preserved as the analytical foundation. The repository now adds a reproducible training pipeline, validation-only threshold optimization, versioned model artifact, typed FastAPI scoring service, container deployment, schema validation, and unit tests.

## Portfolio Snapshot

**Problem:** Fleet failure risk is difficult to operationalize when telemetry contains missing or non-physical values and failure is represented across several component indicators.

**Method:** Normalize the source schema, derive one Fail/Pass target from Failure A-E, preprocess mixed numerical/categorical features, compare three classifiers, tune the operating threshold on validation data with recall-weighted F2, and lock evaluation to an untouched test split.

**Production output:** A serialized preprocessing + model bundle, model/version metadata, threshold-aware online scoring API, liveness/readiness checks, Docker deployment, reproducible metrics, and automated unit tests.

**Stack:** Python · pandas · scikit-learn · FastAPI · Docker · DuckDB

## Why this is now production work

The earlier version intentionally stopped at EDA and target design. The upgraded repository separates exploration from serving and adds the controls needed to move a model through a repeatable lifecycle:

- one training/serving feature contract
- stratified 60/20/20 train/validation/test split
- Logistic Regression, Random Forest, and Gradient Boosting comparison
- ROC-AUC and average-precision ranking metrics
- precision, recall, F1 and recall-weighted F2 operating metrics
- validation-only decision-threshold tuning
- model artifact containing preprocessing, classifier, threshold, features, version and creation time
- FastAPI service that loads the model once and supports bounded batch inference
- `/live`, `/ready`, and `/metadata` operational endpoints
- container execution as a non-root user
- tests for target construction and threshold behavior

## Source schema

The training pipeline expects the fields used by the original notebook:

- `Car ID`
- `Model`
- `Color`
- `Temperature`
- `RPM`
- `Factory`
- `Usage`
- `Fuel consumption`
- `Membership`
- `Failure A` through `Failure E`

The target is defined as failure when **any** Failure A-E flag equals `1`. Identifier and component-failure columns are excluded from model inputs so they cannot leak the target.

## Model features

The service scores these fields:

```text
model
color
temperature
rpm
factory
usage
fuel_consumption
membership
```

Numerical values are median-imputed and standardized. Categorical fields are most-frequent-imputed and one-hot encoded with unknown-category handling.

## Train

The source dataset is intentionally not committed. Place `Failure.csv` locally and run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.train --data Failure.csv
```

Generated artifacts include:

```text
artifacts/model_bundle.joblib
outputs/training_summary.json
outputs/validation_model_comparison.csv
outputs/threshold_tuning.csv
outputs/test_predictions.csv
```

The test split is used only after model and threshold selection are complete.

## Serve

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Operational endpoints:

```text
GET  /live
GET  /ready
GET  /metadata
POST /predict
```

Example request:

```json
[
  {
    "model": "SUV",
    "color": "Blue",
    "temperature": 88.0,
    "rpm": 4200,
    "factory": "Factory B",
    "usage": "Very High",
    "fuel_consumption": 10.2,
    "membership": "Gold"
  }
]
```

The response returns failure probability, binary decision, operating threshold, model name, and model version.

`MAX_BATCH_SIZE` defaults to 100 and can be overridden with an environment variable. `MODEL_PATH` can point the service to a promoted model bundle.

## Docker

```bash
docker build -t vehicle-failure-api .
docker run --rm -p 8000:8000 -v "$PWD/artifacts:/app/artifacts:ro" vehicle-failure-api
```

The image runs as a non-root application user. The container remains live if a model artifact is missing, while `/ready` returns `503`; this separates process health from model readiness.

## Tests

```bash
pytest -q
```

## Original analytical findings

The notebook reported useful EDA signals including higher observed failure rates for very-high-usage vehicles and elevated failure rates in high fuel-consumption segments. Those findings remain exploratory associations, not causal conclusions.

## Production boundary

No new predictive-performance number is claimed in this README because `Failure.csv` is not committed and the upgraded training pipeline has not been rerun here against the source dataset. After training, use `outputs/training_summary.json` as the source of truth for locked test metrics rather than copying notebook-era percentages into model-performance claims.

## Repository structure

```text
.
├── app.py
├── car_failure_analysis.ipynb
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── inference.py
│   ├── pipeline.py
│   └── train.py
└── tests/
    └── test_pipeline.py
```

## Next production steps

Infrastructure outside this repository would still be needed for authentication/authorization, centralized logs and metrics, a managed model registry, scheduled retraining, alert routing, data contracts, canary rollout, rollback automation, and real fleet feedback loops.
