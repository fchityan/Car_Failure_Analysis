# Security Policy

Never commit API keys, cloud credentials, customer data, or private fleet telemetry.

Production deployments should use a secret manager, TLS ingress, `REQUIRE_API_KEY=true`, an immutable `MODEL_SHA256`, read-only model mounts, non-root containers, network policy, gateway rate limits, dependency/container scanning, and image signing.

If a credential is committed accidentally, revoke and rotate it before cleaning Git history.
