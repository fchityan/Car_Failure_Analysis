# Vehicle Failure Risk

## Project Overview

This predictive-maintenance project explores how vehicle attributes and operating conditions relate to equipment-failure risk. It builds on an exploratory car-failure notebook and defines a binary prediction task: whether **any of five component-failure flags** indicates a failure.

## Problem

Vehicle information can contain missing values, inconsistent categories, and extreme readings. A useful classification approach must handle these inputs while reducing the chance of overlooking potentially costly failures.

## Approach

- Combine Failure A–E indicators into a single Fail/Pass target.
- Exclude identifiers and failure flags from prediction features to prevent target leakage.
- Prepare numerical and categorical information with repeatable preprocessing.
- Compare Logistic Regression, Random Forest, and Gradient Boosting.
- Use validation-set F2 to tune the decision threshold, then assess a held-out test set.

## Key Features

- Reproducible vehicle-risk training and evaluation
- Feature-based single and batch predictions through FastAPI
- Input checks, versioned model outputs, and automated tests
- Retained exploratory analysis for investigating possible risk factors

## Findings and Limitations

The exploratory notebook observed higher failure rates in very-high-usage vehicles and some high-fuel-consumption groups. **These are associations, not proof of causation.** No new predictive-performance score is claimed here because the original `Failure.csv` dataset is not committed and the updated training pipeline has not been rerun against it.

## Business Analysis, Digital Transformation & AI Enablement

- **Business analysis:** Define failure-risk requirements, source-field validation, maintenance triage and traceable acceptance criteria.
- **Digital transformation:** Translate exploratory telemetry into a repeatable predictive-maintenance workflow and scoring API.
- **AI enablement:** Assess leakage prevention, recall-weighted evaluation, source-data readiness and model-governance gaps.

See the [requirements and solution-design assessment](docs/business-analysis/business-requirements-and-solution-design.md) and [AI readiness / governance assessment](docs/ai-enablement/ai-readiness-and-model-governance-assessment.md). These documents are analysis artefacts, not claims of formal UAT or enterprise deployment.

### Folder guide

| Existing folder | Business or delivery perspective |
|---|---|
| `app.py` | API scoring and digital solution integration |
| `src/` | Vehicle-data transformation and predictive ML lifecycle |
| `tests/` | Automated model and schema quality checks |
| `deployment-architecture/` | Deployment architecture and operating readiness |
| `docs/` | Requirements analysis, solution design and AI governance |

## Technology Stack

- **Language and analysis:** Python, pandas, NumPy, DuckDB, Jupyter Notebook
- **Machine learning:** scikit-learn (Logistic Regression, Random Forest, Gradient Boosting, preprocessing/evaluation), joblib
- **API and validation:** FastAPI, Uvicorn, Pydantic, HTTPX
- **Monitoring and deployment:** Prometheus Python client, Docker, Kubernetes
- **Testing and automation:** pytest, GitHub Actions CI

## Explore the Project

- [Business analysis, solution design and AI-governance documentation](docs/README.md)

- [Original exploratory notebook](data-discovery-and-insights/fleet-reliability-and-failure-risk-profiling.ipynb)
- [Technical guide — schema, evaluation, and run commands](docs/solution-design/solution-design-and-implementation-guide.md)
- [Deployment and operations notes](docs/operational-readiness/service-transition-and-operations-runbook.md)
- [Security guidance](SECURITY.md)

To reproduce training, provide the source `Failure.csv` and follow the technical guide.
