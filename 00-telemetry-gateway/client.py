"""
Module: client.py
Description: Production-grade high-velocity telemetry simulation client 
             equipped with automatic reconnection backoff logic.
"""
import asyncio
import json
import os
import random
import sys
import time
from pydantic import BaseModel
import websockets

# =====================================================================
# ROOT ALIAS CONFIGURATION (React-Style Absolute Module Resolution)
# =====================================================================
ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_WORKSPACE not in sys.path:
    sys.path.insert(0, ROOT_WORKSPACE)


class TelemetryPayload(BaseModel):
    device_id: str
    engine_temp: float
    rpm: int
    vibration_amplitude: float
    timestamp: float


async def simulate_telemetry_stream():
    url = "ws://127.0.0.1:8000/stream/telemetry"
    device_ids = ["DEV-ALPHA", "DEV-BRAVO", "DEV-CHARLIE"]
    
    print(f"[CLIENT] Target gateway configured at {url}")
    
    while True:
        try:
            print("[CLIENT] Attempting connection to gateway stream...")
            async with websockets.connect(url) as websocket:
                print("[CLIENT] Channel linked! Beginning ingestion run...")
                
                while True:
                    # Generate realistic simulated hardware data structures
                    payload = {
                        "device_id": random.choice(device_ids),
                        "engine_temp": round(random.uniform(70.0, 105.0), 2),
                        "rpm": random.randint(2500, 6800),
                        "vibration_amplitude": round(random.uniform(0.1, 2.5), 4),
                        "timestamp": time.time()
                    }
                    
                    # Serialize and push data over the persistent wire frame
                    await websocket.send(json.dumps(payload))
                    print(f"[SENT] Emitted packet for {payload['device_id']} -> Temp: {payload['engine_temp']}°C | RPM: {payload['rpm']}")
                    
                    # Ingestion frequency tracking (500ms delay window)
                    await asyncio.sleep(0.5)
                    
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as connection_fault:
            print(f"\n[DISCONNECTED] Connection dropped or server reloading ({connection_fault}).")
            print("[RETRY] Waiting 3 seconds before executing reconnection sequence...")
            await asyncio.sleep(3)
            
        except Exception as general_fault:
            print(f"\n[ERROR] Client tracking anomaly encountered: {general_fault}")
            print("[RETRY] Cooling down loop for 3 seconds...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    print("[SYSTEM] Starting Live Player Ingestion Subsystem...")
    try:
        asyncio.run(simulate_telemetry_stream())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Simulation terminated cleanly by user.")