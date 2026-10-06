from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from src.inference import load_model_bundle, predict_records

MODEL_PATH = Path(os.getenv("MODEL_PATH", "artifacts/model_bundle.joblib"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "100"))


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


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.bundle = None
    application.state.load_error = None
    try:
        application.state.bundle = load_model_bundle(MODEL_PATH)
    except Exception as exc:  # readiness should expose missing/bad artifact without killing liveness
        application.state.load_error = str(exc)
    yield


app = FastAPI(title="Vehicle Failure Risk API", version="1.0.0", lifespan=lifespan)


@app.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(request: Request) -> dict[str, str]:
    if request.app.state.bundle is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Model not loaded")
    return {"status": "ready", "model_version": request.app.state.bundle["model_version"]}


@app.get("/metadata")
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
    }


@app.post("/predict", response_model=list[PredictionResponse])
def predict(payload: list[VehicleFeatures], request: Request):
    bundle = request.app.state.bundle
    if bundle is None:
        raise HTTPException(status_code=503, detail=request.app.state.load_error or "Model not loaded")
    if not payload:
        raise HTTPException(status_code=400, detail="At least one vehicle is required.")
    if len(payload) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=413, detail=f"Batch exceeds MAX_BATCH_SIZE={MAX_BATCH_SIZE}.")

    request_id = uuid4().hex
    try:
        predictions = predict_records([record.model_dump() for record in payload], bundle)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for prediction in predictions:
        prediction["request_id"] = request_id
    return predictions
