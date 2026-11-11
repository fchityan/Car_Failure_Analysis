# Fleet Reliability & Failure Risk Data Discovery

**Notebook:** [Fleet Reliability and Failure Risk Profiling](fleet-reliability-and-failure-risk-profiling.ipynb)

An exploratory analysis of vehicle condition, usage and component-failure indicators, intended to inform risk-scoring and potential maintenance triage requirements.

## Input and reproducibility

- The notebook uses DuckDB and expects `Failure.csv` in its **working directory**. The source dataset is not committed.
- It creates a local `failure.db` database from the supplied CSV. Do not commit the generated database or confidential fleet data.
- The reproducible model-training API remains under `../src/`; consult the [Implementation Guide](../docs/solution-design/solution-design-and-implementation-guide.md) for the training and evaluation procedure.
- Exploratory associations are not causal claims. No new predictive performance metrics are asserted without rerunning the updated pipeline against the source data.

See the [Project Overview](../README.md) and [Business Requirements & Solution Design](../docs/business-analysis/business-requirements-and-solution-design.md).
