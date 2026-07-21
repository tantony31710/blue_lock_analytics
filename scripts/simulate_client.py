"""
Simulates 3 devices streaming telemetry to the gateway over WebSocket.
Run this while the FastAPI server (app/main.py) is running, to generate
live traffic for local testing.
"""
import asyncio
import json
import os
import random
import time

import websockets

GATEWAY_URL = "ws://127.0.0.1:8000/stream/telemetry"
DEVICE_IDS = ["DEV-ALPHA", "DEV-BRAVO", "DEV-CHARLIE"]
DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "dev-only-insecure-device-key")


async def stream_forever():
    while True:
        try:
            print("[CLIENT] Connecting to gateway...")
            async with websockets.connect(
                GATEWAY_URL, additional_headers={"x-api-key": DEVICE_API_KEY}
            ) as ws:
                print("[CLIENT] Connected. Streaming...")
                while True:
                    payload = {
                        "device_id": random.choice(DEVICE_IDS),
                        "engine_temp": round(random.uniform(70.0, 105.0), 2),
                        "rpm": random.randint(2500, 6800),
                        "vibration_amplitude": round(random.uniform(0.1, 2.5), 4),
                    }
                    await ws.send(json.dumps(payload))
                    reply = await ws.recv()
                    print(f"[SENT] {payload['device_id']} -> {reply}")
                    await asyncio.sleep(0.5)
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as err:
            print(f"[DISCONNECTED] {err} — retrying in 3s...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(stream_forever())
    except KeyboardInterrupt:
        print("\n[CLIENT] Stopped.")
