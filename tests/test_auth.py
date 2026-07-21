from app.auth import hash_password
from app.storage import StorageManager


def _make_user(db_path, username="tester", password="hunter2"):
    db = StorageManager(db_path=db_path)
    db.initialize_schema()
    db.create_user(username, hash_password(password))
    db.close()


def test_analytics_endpoint_requires_login(client):
    resp = client.get("/api/analytics/watchlist")
    assert resp.status_code == 401


def test_login_with_bad_credentials_fails(client):
    resp = client.post("/api/auth/login", data={"username": "nope", "password": "nope"})
    assert resp.status_code == 401


def test_login_and_access_protected_endpoint(client, monkeypatch):
    import os
    _make_user(os.environ["TELEMETRY_DB_PATH"])

    resp = client.post("/api/auth/login", data={"username": "tester", "password": "hunter2"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/analytics/watchlist", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_telemetry_endpoint_requires_device_key(client):
    resp = client.post(
        "/api/v1/telemetry",
        json={"device_id": "DEV-X", "engine_temp": 80.0, "rpm": 3000, "vibration_amplitude": 0.5},
    )
    assert resp.status_code in (401, 422)  # 422 if FastAPI complains about missing header first


def test_telemetry_endpoint_accepts_valid_device_key(client):
    resp = client.post(
        "/api/v1/telemetry",
        json={"device_id": "DEV-X", "engine_temp": 80.0, "rpm": 3000, "vibration_amplitude": 0.5},
        headers={"x-api-key": "test-device-key"},
    )
    assert resp.status_code == 200
