"""
SQLite persistence layer for telemetry frames.
"""
import os
import sqlite3
from typing import Dict, Any


SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class StorageManager:
    def __init__(self, db_path: str = "telemetry_grid.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

    def initialize_schema(self, schema_path: str = SCHEMA_PATH) -> None:
        """Applies schema.sql (tables, indexes, views). Safe to run repeatedly —
        every statement uses IF NOT EXISTS, so it never destroys existing data."""
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with open(schema_path, "r") as f:
            self.cursor.executescript(f.read())
        self.connection.commit()

    def save_telemetry_frame(self, data_frame: Dict[str, Any]) -> None:
        """Inserts one processed telemetry frame."""
        self.cursor.execute(
            """
            INSERT INTO device_telemetry (device_id, drift_index, status)
            VALUES (?, ?, ?);
            """,
            (data_frame["device_id"], data_frame["drift_index"], data_frame["status"]),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
