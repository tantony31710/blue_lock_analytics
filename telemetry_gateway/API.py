import os
import sys
import json
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# =====================================================================
# ROOT ALIAS CONFIGURATION
# =====================================================================
ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_WORKSPACE not in sys.path:
    sys.path.insert(0, ROOT_WORKSPACE)

# Absolute imports from the new flattened structure
from telemetry_gateway.math_and_stats.Math import calculate_vector_drift
from data_engineering.advanced_sql.storage_manager import StorageManager

# =====================================================================
# ENGINE & BACKEND CORE INITIALIZATION
# =====================================================================
app = FastAPI(
    title="Blue Lock Telemetry Gateway",
    version="0.2.0",
    description="Professional Telemetry Ingestion and Analytics Engine"
)

# Initialize single long-lived database instance
DB_PATH = os.path.join(ROOT_WORKSPACE, "telemetry_grid.db")
db_manager = StorageManager(db_path=DB_PATH)

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
    return {
        "status": "online", 
        "system": "Blue Lock Telemetry Gateway",
        "version": "0.2.0"
    }

@app.get("/api/analytics/watchlist")
def get_watchlist():
    """
    Returns devices with high drift indices for immediate attention.
    Consolidated from legacy Flask analytical server.
    """
    try:
        # Note: Accessing cursor directly for analytical queries
        query = "SELECT device_id, drift_index, status, timestamp FROM device_telemetry WHERE status = 'CRITICAL_ANOMALY' ORDER BY timestamp DESC LIMIT 10"
        db_manager.cursor.execute(query)
        results = db_manager.cursor.fetchall()
        
        watchlist = []
        for row in results:
            watchlist.append({
                "device_id": row[0],
                "drift_index": round(row[1], 2),
                "status": row[2],
                "timestamp": row[3]
            })
        return {"count": len(watchlist), "watchlist": watchlist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/stream/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[SYSTEM] New device linked stream channel established.")
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            try:
                current_metrics = [
                    float(data["engine_temp"]),
                    float(data["rpm"]),
                    float(data["vibration_amplitude"])
                ]
                device_id = data["device_id"]
                
                drift_index = calculate_vector_drift(current_metrics, HEALTHY_BASELINE)
                status = "CRITICAL_ANOMALY" if drift_index > ANOMALY_THRESHOLD else "HEALTHY"
                
                processed_frame = {
                    "device_id": device_id,
                    "drift_index": drift_index,
                    "status": status
                }
                
                db_manager.save_telemetry_frame(processed_frame)
                
                # Push real-time analysis back to client
                await websocket.send_json({
                    "device_id": device_id,
                    "drift_index": round(drift_index, 2),
                    "status": status
                })
                
            except (KeyError, ValueError) as e:
                await websocket.send_json({"error": "MALFORMED_PACKET", "details": str(e)})
    except WebSocketDisconnect:
        print("[SYSTEM] Client connection terminated normally.")
    except Exception as e:
        print(f"[NETWORKING ERROR] Unexpected socket drop: {e}")

@app.post("/api/v1/telemetry")
def receive_telemetry(payload: TelemetryPayload):
    try:
        current_metrics = [
            payload.engine_temp,
            payload.rpm,
            payload.vibration_amplitude
        ]
        drift_index = calculate_vector_drift(current_metrics, HEALTHY_BASELINE)
        status = "CRITICAL_ANOMALY" if drift_index > ANOMALY_THRESHOLD else "HEALTHY"
        
        processed_frame = {
            "device_id": payload.device_id,
            "drift_index": drift_index,
            "status": status
        }
        
        db_manager.save_telemetry_frame(processed_frame)
        return {
            "status": "PROCESSED", 
            "drift_index": round(drift_index, 4), 
            "system_state": status
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

if __name__ == "__main__":
    uvicorn.run("telemetry_gateway.API:app", host="0.0.0.0", port=8000, reload=True)
