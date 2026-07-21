import os
import tempfile

import pytest


@pytest.fixture
def client():
    """Fresh app + temp database per test, so tests never share state."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["TELEMETRY_DB_PATH"] = db_path
    os.environ["DEVICE_API_KEY"] = "test-device-key"
    os.environ["JWT_SECRET_KEY"] = "test-secret"

    # Import after env vars are set, and force a fresh module each time
    # so main.py's module-level db_manager picks up the temp db path.
    import sys
    for mod in list(sys.modules):
        if mod.startswith("app."):
            del sys.modules[mod]

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    os.remove(db_path)
