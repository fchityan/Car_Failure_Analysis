# Business Requirements, Stakeholders & Traceability — Vehicle Failure Risk

**Document control:** v0.1 portfolio reference; owner, version approval, issue date and change-control board are **not established**. No customer-approved BRD exists.

## Business purpose and measures
**Problem:** Fleet component failures are recorded across Failure A–E flags and operating attributes. A risk score could support earlier technician review but must not trigger unreviewed maintenance decisions.

**Potential users:** fleet operations owner, reliability engineer, maintenance planner, business analyst, data steward and AI engineer; none are confirmed project signatories.

**Illustrative As-Is:** manual exploration of vehicle features and failure indicators. **Reference To-Be:** source validation → leakage-safe features → comparison of models → validation-selected recall-oriented threshold → human review of candidate failures → maintenance decision recorded outside the model.

**Candidate business metrics (unmeasured):** missed-failure rate; false alarms per 100 alerts; technician review time; vehicle downtime avoided; cost per reviewed alert. Baseline, target, cost assumptions and decision authority require owner agreement.

## Requirements traceability (proposed; not signed off)
| ID | Priority | Requirement | Repository evidence | Proposed verification |
|---|---|---|---|---|
| BR-01 | Must | Define failure as any positive Failure A–E flag | `src/pipeline.py`, original notebook | Compare target label with hand-calculated examples |
| FR-01 | Must | Remove target flags and identifiers from predictors | Pipeline feature preparation | Automated negative-feature assertion |
| FR-02 | Must | Handle missing and invalid numerical/categorical values | Preprocessing and API validation | Missing-value and malformed-input tests |
| FR-03 | Must | Benchmark Logistic Regression, Random Forest and Gradient Boosting | `src/train.py` | Reproduce validation comparison from approved data |
| FR-04 | Must | Select a recall-sensitive operating threshold without test leakage | Validation F2 workflow | Confirm final test data never selects threshold |
| FR-05 | Should | Expose traceable single/batch risk scores for review | `app.py`, model bundle | Positive/negative API contract examples |
| NFR-01 | Must | Preserve model version, schema, threshold and integrity fingerprint | Model metadata; reference runbook | Confirm version/fingerprint in response and release record |
| NFR-02 | Must | Define reviewer override, change control and incident owner | **Not evidenced as deployed** | Signed operating procedure before pilot |

## Ownership and decisions still required
| Decision | Proposed accountable role | Status |
|---|---|---|
| Definition/cost of failure and alert threshold | Fleet operations owner | Open |
| Dataset provenance, usage rights and quality threshold | Data steward | Open |
| Review workflow and human override | Maintenance lead | Open |
| Security, access and retention policy | Security/privacy lead | Open |
| Pilot pass/fail and release approval | Sponsor/change authority | Open |

## Acceptance boundaries
The existing tests and code are useful *engineering evidence*, not stakeholder UAT. A pilot needs agreed scenarios including unseen failure flags, implausible sensor readings, missing features, delayed labels, false-positive review volume and operator overrides. Record expected results, observed results, test executor, date, defect references and sign-off separately; no such signed record is asserted here.
