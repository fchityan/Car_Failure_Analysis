# Car Failure Analysis

Business-focused exploratory analysis of vehicle failure risk, designed to support preventive maintenance decisions and prepare a machine-learning-ready classification target.

## Executive Summary

Unexpected vehicle failures increase downtime, maintenance cost, and operational disruption. This project translates raw fleet-style data into decision-ready insights and a clear Fail or Pass target for downstream predictive modeling.

## Business Objective

Identify which vehicle segments and operating conditions are most associated with failure so maintenance teams can intervene earlier and allocate resources more effectively.

## Competencies Demonstrated

- SQL-first analytics using DuckDB in Python.
- Data quality diagnosis and practical imputation strategy.
- Feature engineering for interpretability and stakeholder communication.
- Translation of technical analysis into business-facing recommendations.

## Technical Scope

- Ingest Failure.csv into DuckDB as the analytical working table.
- Audit null and non-physical values in key fields.
- Standardize schema and column naming for maintainable SQL workflows.
- Impute invalid RPM, temperature, and fuel consumption using model-level medians.
- Recode missing membership values to No Membership.
- Engineer binary target label.
- Engineer interpretable risk-band features.
- Quantify failure patterns by model, factory, usage, membership, and operating conditions.

## Target Definition

- Fail: at least one of failure_a, failure_b, failure_c, failure_d, failure_e equals 1.
- Pass: all failure indicators equal 0.

## Key Findings

- Class distribution is suitable for binary modeling, with Fail at 35.85% and Pass at 64.15%.
- SUV is the highest-risk model segment with a 38.24% failure rate.
- Factory B shows the highest factory-level failure rate at 38.15%.
- Very high usage has the strongest association with failure at 71.36%.
- High fuel-consumption vehicles show elevated failure rates at 42.28%.

## Business Implications

- Prioritize preventive checks for high-usage and high fuel-consumption vehicles.
- Use model and factory risk segmentation to support maintenance planning.
- Incorporate engineered risk bands into predictive maintenance scoring.

## Limitations

- Analysis is observational and does not establish causality.
- Feature interactions and confounding factors are not yet modeled.
- Some subgroup-level percentages may be unstable due to small sample sizes.
- Current scope ends at EDA and target design, without trained models.

## Recommended Next Steps

- Train baseline classifiers on the engineered target.
- Evaluate with ROC-AUC, precision, recall, F1, and confusion matrix.
- Add cross-validation and threshold tuning for decision quality.
- Perform explainability analysis to support stakeholder trust.
- Refactor notebook logic into reusable, testable pipelines.

## Tech Stack

- Python
- DuckDB
- pandas
- SQL

## Repository Contents

- car_failure_analysis.ipynb
- README.md


## Project Summary

This project demonstrates end-to-end analytical ownership: defining a business problem, cleaning imperfect data, engineering interpretable features, quantifying risk patterns, and outlining a practical path to production-ready predictive modeling.
