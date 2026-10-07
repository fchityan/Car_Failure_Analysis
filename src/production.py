from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

LOGGER = logging.getLogger("vehicle_failure_api")

REQUEST_COUNT = Counter(
    "vehicle_failure_http_requests_total",
    "HTTP requests handled by the vehicle failure service.",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "vehicle_failure_http_request_duration_seconds",
    "HTTP request latency for the vehicle failure service.",
    ["method", "path"],
)
MODEL_INFO = Gauge(
    "vehicle_failure_model_info",
    "Loaded model metadata.",
    ["model_name", "model_version"],
)


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format="%(message)s")


def artifact_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_model_artifact(path: str | Path) -> str:
    actual = artifact_sha256(path)
    expected = os.getenv("MODEL_SHA256", "").strip().lower()
    if expected and not hmac.compare_digest(actual.lower(), expected):
        raise ValueError("Model artifact SHA-256 does not match MODEL_SHA256.")
    return actual


def register_model_metrics(model_name: str, model_version: str) -> None:
    MODEL_INFO.labels(model_name=model_name, model_version=model_version).set(1)


def require_api_key(request: Request) -> None:
    configured = os.getenv("API_KEY", "")
    required = _truthy(os.getenv("REQUIRE_API_KEY", "false"))
    if not required and not configured:
        return
    if not configured:
        raise HTTPException(status_code=503, detail="API authentication is required but API_KEY is not configured.")
    provided = request.headers.get("x-api-key", "")
    if not provided or not hmac.compare_digest(provided, configured):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def install_observability(app) -> None:
    @app.middleware("http")
    async def observe_request(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = "no-store"
            return response
        finally:
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            duration = time.perf_counter() - started
            REQUEST_COUNT.labels(request.method, route_path, str(status)).inc()
            REQUEST_LATENCY.labels(request.method, route_path).observe(duration)
            LOGGER.info(json.dumps({
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": route_path,
                "status": status,
                "duration_ms": round(duration * 1000, 3),
                "service_env": os.getenv("SERVICE_ENV", "development"),
            }, separators=(",", ":")))
