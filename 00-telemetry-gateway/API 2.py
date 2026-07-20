import asyncio
import json
import random
import time
import websockets
import uvicorn

# --- SIMULATION CONFIGURATION ---
GATEWAY_URL = "ws://localhost:8000/stream/telemetry"
DEVICE_IDS = ["ESP32_CAM_01", "ESP32_CAM_02", "ESP32_CAM_03"]

async def run_device_stream(device_id: str):
    """Simulates a single ESP32 microcontroller streaming live telemetry."""
    async for websocket in websockets.connect(GATEWAY_URL):
        try:
            print(f"[{device_id}] Stream pipeline established with gateway.")
            
            # Continuous streaming loop
            while True:
                # Generate realistic engine/hardware mechanics data
                payload = {
                    "device_id": device_id,
                    "engine_temp": round(random.uniform(70.0, 105.0), 2),
                    "rpm": random.randint(2500, 6500),
                    "vibration_amplitude": round(random.uniform(0.1, 4.5), 4),
                    "timestamp": time.time()
                }
                
                # Turn payload into a text frame string and transmit
                await websocket.send(json.dumps(payload))
                
                # High frequency transmit delay: 200ms interval (5 packets/sec per device)
                await asyncio.sleep(0.2)
                
        except websockets.ConnectionClosed:
            print(f"[{device_id}] Stream severed. Attempting reconnect...")
            await asyncio.sleep(2)  # Reconnection backoff
            continue

async def main():
    # Spin up all simulated ESP32 streams concurrently in the event loop
    stream_tasks = [run_device_stream(d_id) for d_id in DEVICE_IDS]
    await asyncio.gather(*stream_tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Simulation terminated by architect.")