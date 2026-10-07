from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from src.inference import load_model_bundle, predict_records
from src.production import (
    configure_logging,
    install_observability,
    metrics_response,
    register_model_metrics,
    require_api_key,
    verify_model_artifact,
)

MODEL_PATH = Path(os.getenv("MODEL_PATH", "artifacts/model_bundle.joblib"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "100"))
DOCS_ENABLED = os.getenv("ENABLE_DOCS", "true").lower() in {"1", "true", "yes", "on"}

configure_logging()


class VehicleFeatures(BaseModel):
    model: str = Field(min_length=1)
    color: str = Field(min_length=1)
    temperature: float = Field(gt=0)
    rpm: float = Field(gt=0)
    factory: str = Field(min_length=1)
    usage: str = Field(min_length=1)
    fuel_consumption: float = Field(gt=0)
    membership: str = Field(min_length=1)


class PredictionResponse(BaseModel):
    failure_probability: float = Field(ge=0.0, le=1.0)
    predicted_failure: int
    threshold: float
    model_name: str
    model_version: str
    request_id: str


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.bundle = None
    application.state.load_error = None
    application.state.model_sha256 = None
    try:
        application.state.model_sha256 = verify_model_artifact(MODEL_PATH)
        application.state.bundle = load_model_bundle(MODEL_PATH)
        register_model_metrics(application.state.bundle["model_name"], application.state.bundle["model_version"])
    except Exception as exc:
        application.state.load_error = str(exc)
    yield


app = FastAPI(
    title="Vehicle Failure Risk API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url="/redoc" if DOCS_ENABLED else None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
)
install_observability(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "vehicle-failure-risk", "version": app.version}


@app.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(request: Request) -> dict[str, str]:
    if request.app.state.bundle is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Model not loaded")
    return {
        "status": "ready",
        "model_version": request.app.state.bundle["model_version"],
        "service_env": os.getenv("SERVICE_ENV", "development"),
    }


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.get("/metadata", dependencies=[Depends(require_api_key)])
def metadata(request: Request) -> dict[str, Any]:
    bundle = request.app.state.bundle
    if bundle is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Model not loaded")
    return {
        "model_name": bundle["model_name"],
        "model_version": bundle["model_version"],
        "threshold": bundle["threshold"],
        "feature_columns": bundle["feature_columns"],
        "created_at_utc": bundle.get("created_at_utc"),
        "model_sha256": request.app.state.model_sha256,
        "service_env": os.getenv("SERVICE_ENV", "development"),
    }


@app.post("/predict", response_model=list[PredictionResponse], dependencies=[Depends(require_api_key)])
def predict(payload: list[VehicleFeatures], request: Request):
    bundle = request.app.state.bundle
    if bundle is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Model not loaded")
    if not payload:
        raise HTTPException(status_code=400, detail="At least one vehicle is required.")
    if len(payload) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=413, detail=f"Batch exceeds MAX_BATCH_SIZE={MAX_BATCH_SIZE}.")
    try:
        predictions = predict_records([record.model_dump() for record in payload], bundle)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    request_id = getattr(request.state, "request_id", "")
    for prediction in predictions:
        prediction["request_id"] = request_id
    return predictions
