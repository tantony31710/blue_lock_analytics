import os
import tempfile

import pytest

from app.storage import StorageManager


@pytest.fixture
def storage():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    manager = StorageManager(db_path=path)
    manager.initialize_schema()
    yield manager
    manager.close()
    os.remove(path)


def test_schema_creates_expected_tables(storage):
    cursor = storage.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "device_telemetry" in tables
    assert "hourly_device_summaries" in tables
    assert "daily_exposure_logs" in tables


def test_save_and_read_telemetry_frame(storage):
    storage.save_telemetry_frame({"device_id": "DEV-TEST", "drift_index": 12.5, "status": "HEALTHY"})
    cursor = storage.connection.cursor()
    cursor.execute("SELECT device_id, drift_index, status FROM device_telemetry")
    row = cursor.fetchone()
    assert row == ("DEV-TEST", 12.5, "HEALTHY")
