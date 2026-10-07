# Production Runbook

The repository now implements production-style controls at the application and MLOps layer. A live production claim still requires an actual deployment, real fleet telemetry, and operational ownership.

## Release flow

1. Train with `python -m src.train --data Failure.csv`.
2. Review validation comparison, threshold tuning, locked test metrics, and `outputs/deployment_manifest.json`.
3. Promote an immutable `artifacts/model_bundle.joblib`.
4. Store the promoted SHA-256 and API key in the platform secret manager.
5. Deploy the container behind TLS ingress/API gateway.
6. Verify `/live`, `/ready`, `/metrics`, then run a known-good prediction smoke test.

Never overwrite a promoted artifact in place. A new training run should produce a new model version and fingerprint.

## Runtime controls

- `/live`: process health.
- `/ready`: model-loaded readiness.
- `/metrics`: Prometheus request count, latency, and model-info metrics.
- `/metadata`: authenticated model metadata including the loaded artifact fingerprint.
- `/predict`: authenticated bounded-batch inference.
- Every response carries `X-Request-ID`.
- Logs are structured JSON and omit request payloads.
- `MODEL_SHA256` optionally enforces immutable artifact integrity.
- `ENABLE_DOCS=false` removes public OpenAPI/Swagger endpoints in production.

## Suggested SLO targets

These are targets to measure after deployment, not measured claims:

- 99.9% monthly availability.
- p95 single-record service latency below 150 ms under normal load.
- 5xx rate below 0.5% over a 15-minute window.
- zero traffic to a pod until the promoted model passes readiness.

## Alerts

Alert on sustained readiness failure, 5xx spikes, p95 latency breaches, model checksum mismatch, unusual schema rejection rate, and material degradation in real outcome metrics.

## Rollback

Roll back both image and model artifact to the previous immutable versions. Keep previous deployment manifests and fingerprints. Kubernetes rollout history plus the artifact registry should provide the audit trail.

## Real-world integrations still required

A hosting environment must supply centralized logs/traces, cloud IAM, managed secrets, model/artifact registry, ingress rate limiting/WAF, image signing/scanning, alert routing, real telemetry ingestion, outcome feedback, and an on-call owner.
