"""
Module: API.py
Description: Central Telemetry Gateway API utilizing absolute root imports 
             to process high-frequency real-time WebSocket telemetry packets.
"""
import os
import sys
import json
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import uvicorn

# =====================================================================
# ROOT ALIAS CONFIGURATION (React-Style Absolute Module Resolution)
# =====================================================================
# Injects the base project directory so all paths evaluate from the root tree
ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_WORKSPACE not in sys.path:
    sys.path.insert(0, ROOT_WORKSPACE)

# Clean, declarative absolute imports mapping directly to your roadmap layout
from math_and_stats.Math import calculate_vector_drift
from advanced_sql.storage_manager import StorageManager


# =====================================================================
# ENGINE & BACKEND CORE INITIALIZATION
# =====================================================================
app = FastAPI(
    title="Blue Lock Telemetry Gateway",
    version="0.1.0"
)

# Initialize single long-lived database instance to avoid connection pool exhaustion
db_manager = StorageManager(db_path="telemetry_grid.db")

# Analytics Configuration Parameters
HEALTHY_BASELINE = [75.0, 3000.0, 0.5]
ANOMALY_THRESHOLD = 50.0


# =====================================================================
# DATA SCHEMA VALIDATION LAYER
# =====================================================================
class TelemetryPayload(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=20)
    engine_temp: float = Field(..., ge=-50.0, le=250.0)
    rpm: int = Field(..., ge=0, le=12000)
    vibration_amplitude: float = Field(..., ge=0.0)


# =====================================================================
# REST & WEBSOCKET ROUTING LAYER
# =====================================================================
@app.get("/")
def read_root():
    return {"status": "online", "system": "Blue Lock Telemetry Gateway"}


@app.websocket("/stream/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """
    Accepts incoming persistent streaming channels, extracts metric packets,
    evaluates drift matrices in real-time, and flushes directly to relational storage.
    """
    await websocket.accept()
    print("[SYSTEM] New device linked stream channel established.")
    
    try:
        while True:
            # 1. Receive incoming raw message from WebSocket wire
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            try:
                # 2. Map and format input metrics into vector layout
                current_metrics = [
                    float(data["engine_temp"]),
                    float(data["rpm"]),
                    float(data["vibration_amplitude"])
                ]
                device_id = data["device_id"]
                
                # 3. Process algorithmic analysis via Math core
                drift_index = calculate_vector_drift(current_metrics, HEALTHY_BASELINE)
                status = "CRITICAL_ANOMALY" if drift_index > ANOMALY_THRESHOLD else "HEALTHY"
                
                # 4. Construct production relational structure array
                processed_frame = {
                    "device_id": device_id,
                    "drift_index": drift_index,
                    "status": status
                }
                
                # 5. Persist immediately to disk database storage
                db_manager.save_telemetry_frame(processed_frame)
                print(f"[INGESTED & SAVED] {device_id} -> Drift: {drift_index:.2f} | Status: {status}")
                
            except KeyError as missing_key:
                print(f"[MALFORMED PACKET] Missing expected validation field: {missing_key}")
            except Exception as processing_err:
                print(f"[PIPELINE ERROR] Operational matrix fault: {processing_err}")
                
    except WebSocketDisconnect:
        print("[SYSTEM] Client connection terminated normally.")
    except Exception as network_err:
        print(f"[NETWORKING ERROR] Unexpected socket drop: {network_err}")


@app.post("/api/v1/telemetry")
def receive_telemetry(data: Dict[str, Any]):
    """
    Fallback REST testing endpoint mimicking the core internal engine logic.
    """
    try:
        current_metrics = [
            float(data["engine_temp"]),
            float(data["rpm"]),
            float(data["vibration_amplitude"])
        ]
        drift_index = calculate_vector_drift(current_metrics, HEALTHY_BASELINE)
        status = "CRITICAL_ANOMALY" if drift_index > ANOMALY_THRESHOLD else "HEALTHY"
        
        processed_frame = {
            "device_id": data["device_id"],
            "drift_index": drift_index,
            "status": status
        }
        db_manager.save_telemetry_frame(processed_frame)
        return {"status": "PROCESSED", "drift_index": round(drift_index, 4), "system_state": status}
    except Exception as err:
        return {"status": "PIPELINE_ERROR", "details": str(err)}


if __name__ == "__main__":
    uvicorn.run("API:app", host="127.0.0.1", port=8000, reload=True)