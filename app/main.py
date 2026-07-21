"""
Blue Lock Analytics — telemetry gateway + analytics API.

Single FastAPI service: ingests device telemetry over WebSocket/REST,
scores it against a healthy baseline, persists it, and serves the
aggregated analytics views the frontend reads.
"""
import json
import os
from typing import List

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.auth import authenticate_user, create_access_token, get_current_username
from app.device_auth import verify_device_key, verify_device_key_ws
from app.math_engine import calculate_vector_drift
from app.storage import StorageManager

app = FastAPI(title="Blue Lock Analytics", version="1.0.0")

# Frontend runs on a different port (Vite dev server) — allow it to call this API.
# Tighten allow_origins to your real frontend URL before deploying publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.environ.get("TELEMETRY_DB_PATH", "telemetry_grid.db")
db_manager = StorageManager(db_path=DB_PATH)
db_manager.initialize_schema()

HEALTHY_BASELINE = [75.0, 3000.0, 0.5]  # [engine_temp, rpm, vibration_amplitude]
ANOMALY_THRESHOLD = 50.0


class TelemetryPayload(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=20)
    engine_temp: float = Field(..., ge=-50.0, le=250.0)
    rpm: int = Field(..., ge=0, le=12000)
    vibration_amplitude: float = Field(..., ge=0.0)


def score_payload(payload: TelemetryPayload) -> dict:
    metrics = [payload.engine_temp, payload.rpm, payload.vibration_amplitude]
    drift_index = calculate_vector_drift(metrics, HEALTHY_BASELINE)
    status = "CRITICAL_ANOMALY" if drift_index > ANOMALY_THRESHOLD else "HEALTHY"
    return {"device_id": payload.device_id, "drift_index": drift_index, "status": status}


@app.get("/")
def read_root():
    return {"status": "online", "system": "Blue Lock Analytics"}


@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db_manager, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(user["username"])
    return {"access_token": token, "token_type": "bearer"}


@app.websocket("/stream/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    if not verify_device_key_ws(websocket):
        await websocket.close(code=4401)  # custom close code = unauthorized
        return
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                payload = TelemetryPayload(**json.loads(raw_data))
            except (json.JSONDecodeError, ValueError) as parse_err:
                await websocket.send_text(json.dumps({"status": "rejected", "reason": str(parse_err)}))
                continue

            frame = score_payload(payload)
            db_manager.save_telemetry_frame(frame)
            await websocket.send_text(json.dumps({"status": "ok", **frame}))
    except WebSocketDisconnect:
        pass


@app.post("/api/v1/telemetry", dependencies=[Depends(verify_device_key)])
def receive_telemetry(payload: TelemetryPayload):
    frame = score_payload(payload)
    db_manager.save_telemetry_frame(frame)
    return {"status": "PROCESSED", "drift_index": round(frame["drift_index"], 4), "system_state": frame["status"]}


def _query_view(view_name: str) -> List[dict]:
    cursor = db_manager.connection.cursor()
    cursor.execute(f"SELECT * FROM {view_name}")
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@app.get("/api/analytics/daily-health")
def get_daily_health(username: str = Depends(get_current_username)):
    try:
        return {"status": "success", "data": _query_view("view_daily_device_health")}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/api/analytics/watchlist")
def get_watchlist(username: str = Depends(get_current_username)):
    try:
        return {"status": "success", "data": _query_view("view_critical_risk_watchlist")}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/api/analytics/drift-spikes")
def get_drift_spikes(username: str = Depends(get_current_username)):
    try:
        return {"status": "success", "data": _query_view("view_hourly_drift_spikes")}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
