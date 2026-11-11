# Business Requirements & Solution Design Specification — Vehicle Failure Risk

Project-facing **requirements and solution-design notes**, not a customer-approved BRD or UAT sign-off.

## Business case and process mapping

**Objective:** Assess failure risk using vehicle characteristics and operating signals to support possible fleet maintenance decisions. The project derives a binary Fail/Pass target from component flags **Failure A–E**.

**Potential stakeholders:** fleet operations owner, maintenance planner, business analyst, reliability engineer and AI engineer.

**Possible As-Is → implemented To-Be:** Manual exploration of vehicle data → consistent schema/target definition → leakage-safe feature preparation → model benchmarking → validation-based F2 threshold tuning → held-out evaluation → versioned API scoring.

## Requirements Traceability Matrix

| ID | Business / functional requirement | Repository evidence | Suggested acceptance check |
|---|---|---|---|
| BR-01 | Define failure consistently | Original notebook; `src/pipeline.py` | Any positive Failure A–E flag produces the failure target |
| FR-01 | Prevent leakage from identifiers and outcome fields | Data preparation | Confirm IDs and component-failure columns are excluded from predictors |
| FR-02 | Handle numerical and categorical values consistently | `src/pipeline.py` | Test missing fields and unexpected categories |
| FR-03 | Benchmark candidate models and prioritize missed failures | `src/train.py` | Review Logistic Regression, Random Forest, Gradient Boosting and F2 thresholding |
| FR-04 | Provide risk-scoring interface | `app.py` | Check valid/invalid API payloads |
| NFR-01 | Keep evaluation reproducible | Tests and model metadata | Verify validation/test separation and versioned results |

The acceptance checks above are **proposed business-analysis scenarios**, not completed UAT.

## Digital transformation considerations

A real predictive-maintenance workflow needs sensor-data integration, maintenance-work-order ownership, failure labels, escalation thresholds, false-alarm analysis, SLA definition and an operator override process. The source `Failure.csv` is not committed; the newer pipeline has not been rerun on it here.

See [AI readiness](../ai-enablement/ai-readiness-and-model-governance-assessment.md).
