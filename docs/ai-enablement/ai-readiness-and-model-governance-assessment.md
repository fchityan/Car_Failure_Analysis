# AI Readiness & Model Governance Assessment — Vehicle Failure Risk

## Data and model readiness

The reference pipeline combines component-failure flags into a single target and excludes target/identifier fields from prediction inputs. It compares Logistic Regression, Random Forest and Gradient Boosting, using a recall-weighted F2 decision threshold selected on validation data.

**Evidence boundary:** The source `Failure.csv` dataset is not in the repository. The enhanced training pipeline has not been rerun here against that dataset, so **no new predictive-performance metric is claimed**. Notebook associations with usage and fuel consumption are exploratory, not causal.

## Governance and validation matrix

| Control | Repository evidence | Requirement before business use |
|---|---|---|
| Data quality | Feature schema and preprocessing | Agreed physical-range rules, completeness and sensor provenance |
| Leakage prevention | Combined target and input exclusions | Independently review feature timing and causal availability |
| Evaluation | Validation threshold and held-out test workflow | Verified source-data test metrics and out-of-time validation |
| Serving | Model bundle and FastAPI interface | Controlled integration, access management and operational testing |
| Monitoring | Reference service/metrics components | Fleet telemetry drift, missed-failure review and accountable alerts |
| Human oversight | Model output as decision support | Technician escalation, overrides and failure-cost policy |

**AI enablement status:** suitable for technical review and controlled pilot planning; **not independently validated for fleet production operations**.

See [requirements and solution design](../business-analysis/business-requirements-and-solution-design.md).
