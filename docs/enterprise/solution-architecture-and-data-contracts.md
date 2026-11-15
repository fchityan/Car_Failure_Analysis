# Solution Architecture, Data Contract & Technical Decisions — Vehicle Failure Risk

**Status:** Documented reference architecture; integration with real fleet telemetry has **not** been validated.

## Logical system flow
```text
Authorised vehicle data / Failure.csv (not committed)
  → schema checks & input normalization
  → derive Fail/Pass from Failure A–E
  → exclude IDs and target flags; impute/encode features
  → stratified training / validation / held-out test
  → LR / Random Forest / Gradient Boosting
  → validation F2 threshold; locked evaluation
  → versioned preprocessing + model + threshold bundle
  → authenticated FastAPI score → technician review (proposed)
  → service/model monitoring, incident and feedback (proposed)
```
The source dataset and complete deployed end-to-end flow are not present as a verified live system. See [implementation guide](../solution-design/solution-design-and-implementation-guide.md) for current commands and repository structure.

## Data contract decisions
| Area | Reference requirement | Open evidence or decision |
|---|---|---|
| Source | `Failure.csv` supplied by an authorised owner | Dataset lineage, timestamp semantics, permitted use |
| Label | Boolean Fail/Pass based on any Failure A–E positive | Label observation time; what is knowable at prediction time |
| Predictors | Vehicle operating attributes, excluding outcome flags and identifiers | Exact production schema, type/range catalogue and units |
| Missing values | Pipeline preprocessing rather than silent row deletion | Acceptance ranges, quarantine thresholds and data quality SLA |
| Output | Risk class/score, selected threshold, model/version metadata | User-facing interpretation, alert handoff and overrides |
| Retention | Minimum fields needed for reproducible audit | Owner-approved retention schedule and access controls |

**Contract validation before pilot:** document feature name, type, unit, nullable rule, source, arrival timing and permitted usage; reject unexpected schema shifts; verify target leakage both in feature selection and time ordering. This table is not a certified production schema.

## Architecture decisions
- **ADR-PM-01 — Recall-weighted F2 on validation:** prioritises potentially missed failures for review. Revisit with real missed-failure and false-alert costs.
- **ADR-PM-02 — Holdout isolation:** no threshold or hyperparameter changes after locked-test evaluation.
- **ADR-PM-03 — Human-led action:** model output informs maintenance prioritisation; no unattended service/repair action.
- **ADR-PM-04 — Immutable releases:** document model fingerprint, code/data version and rollback artifact before promotion.
- **ADR-PM-05 — Reference hosting:** Docker/Kubernetes and FastAPI are engineering patterns, not proof of running fleet infrastructure.

## Integration assumptions
Potential upstream telemetry ingestion and downstream maintenance work orders are **future integrations**. Define interfaces, retries, duplicate-event policy, timeout, API authentication, owner/operator SLAs and failure-mode handling before implementation.
