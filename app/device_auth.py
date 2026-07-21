"""
Device authentication for telemetry ingestion — a shared API key,
not a login. Devices aren't people; a static secret per fleet
(or per device, if you outgrow this) is the standard pattern here,
not a username/password/JWT flow.
"""
import os

from fastapi import Header, HTTPException, WebSocket, status

DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "dev-only-insecure-device-key")


def verify_device_key(x_api_key: str = Header(...)) -> None:
    """Dependency for REST endpoints."""
    if x_api_key != DEVICE_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device API key")


def verify_device_key_ws(websocket: WebSocket) -> bool:
    """Manual check for the WebSocket endpoint (headers work differently there)."""
    key = websocket.headers.get("x-api-key")
    return key == DEVICE_API_KEY
