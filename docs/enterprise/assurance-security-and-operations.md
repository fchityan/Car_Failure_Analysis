# Verification, Model Governance, Security & Operating Readiness — Vehicle Failure Risk

**Evidence status:** Existing repository code/tests and reference monitoring/runbook are *documented*; this checklist is *proposed*; real source-data rerun, fleet UAT, independent security assessment and production operating metrics are *not evidenced*.

## Test strategy and release gates
| Gate | Acceptance evidence required | Current disposition |
|---|---|---|
| Source qualification | Data owner, sample population, provenance, label timing and data dictionary | Open; `Failure.csv` not committed |
| Functional/data | Unit tests for labels, non-physical values, missing columns, feature exclusions | Code/tests documented; current execution unverified |
| Model | Reproduce baseline and candidate comparison, validation F2 and untouched-test metrics | Open for verified source dataset |
| Robustness/fairness | Time-based and subgroup testing; calibration; model drift limits | Proposed |
| API | Invalid payload, auth denial, batch caps, latency and health endpoints | Reference implementation; deployment test open |
| Business UAT | Operator reviews true/false alerts and records decisions | Not performed/recorded |
| Approval | Named sponsor + data, security, model-risk and operations sign-offs | Not evidenced |

## Model risk register
| Risk | Impact | Proposed control | Accountable role (to appoint) |
|---|---|---|---|
| Future failure information leaks into predictors | Inflated metrics and unsafe prioritisation | Time-aware feature and label audit | Model owner |
| Alert overload / missed failures | Operational harm | Cost-sensitive threshold and periodic recall/precision review | Fleet owner |
| Data drift or invalid physical values | Unreliable scoring | Schema/range quarantine and drift alert with triage | Data steward |
| Model artifact tampering | Untrusted inference | SHA-256 pinning, signed release, restricted registry | Platform security |
| Misuse of predicted risk as automatic decision | Inappropriate maintenance action | Explainable human-review gate and override policy | Operations owner |

## Security & privacy design (proposed)
Require least-privilege credentials, TLS at the gateway, secret manager, dependency/image scanning, access log redaction, retention controls, service-account rotation and incident notification ownership. Existing repo references `MODEL_SHA256`, API credentials and structured logging; these are not independently audited security controls.

## Operating model and incident response
**Proposed roles:** sponsor (business KPI), platform owner (availability), model owner (performance), data steward (source quality), on-call responder (incidents). Assign names and escalation routes before pilot.

**Runbook flow:** identify anomaly → classify severity (service unavailable / incorrect high-risk output / drift) → suspend automated recommendations → route to human manual procedure → contain & roll back image + model bundle → validate recovery → log root cause and corrective action.

**Suggested monitoring:** service availability, 5xx, latency p95, invalid-schema rate, feature drift, alert volume, verified false alarms and delayed missed-failure rate. Reference [operational runbook](../operational-readiness/service-transition-and-operations-runbook.md) for illustrative thresholds; no measured SLO claim is made.

## Handover checklist
Data contract signed; tests executed with timestamped evidence; owner-approved acceptance cases; threat review; model card; monitoring dashboards; severity/on-call matrix; release/rollback rehearsal; user training; decommission/retention plan. **All are gates to be satisfied, not items claimed complete.**
