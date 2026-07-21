"""
Persistence layer for telemetry frames and user accounts.
"""
import os
from typing import Any, Dict, Optional

from app.db import IS_POSTGRES, adapt_query, get_connection

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    "postgres_schema.sql" if IS_POSTGRES else "schema.sql",
)


class StorageManager:
    def __init__(self, db_path: str = "telemetry_grid.db"):
        self.connection = get_connection(db_path)
        self.cursor = self.connection.cursor()

    def initialize_schema(self, schema_path: str = SCHEMA_PATH) -> None:
        """Applies the schema (tables, indexes, views). Safe to run repeatedly —
        every statement uses IF NOT EXISTS / OR REPLACE, so it never destroys data."""
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with open(schema_path, "r") as f:
            script = f.read()
        if IS_POSTGRES:
            # psycopg2 has no executescript(); split on statement terminators instead.
            for statement in filter(None, (s.strip() for s in script.split(";"))):
                self.cursor.execute(statement)
        else:
            self.cursor.executescript(script)
        self.connection.commit()

    def save_telemetry_frame(self, data_frame: Dict[str, Any]) -> None:
        self.cursor.execute(
            adapt_query(
                "INSERT INTO device_telemetry (device_id, drift_index, status) VALUES (?, ?, ?);"
            ),
            (data_frame["device_id"], data_frame["drift_index"], data_frame["status"]),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    # ---- user accounts (dashboard login) ----

    def create_user(self, username: str, hashed_password: str) -> None:
        self.cursor.execute(
            adapt_query("INSERT INTO users (username, hashed_password) VALUES (?, ?);"),
            (username, hashed_password),
        )
        self.connection.commit()

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        self.cursor.execute(
            adapt_query("SELECT id, username, hashed_password FROM users WHERE username = ?;"),
            (username,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return {"id": row[0], "username": row[1], "hashed_password": row[2]}
