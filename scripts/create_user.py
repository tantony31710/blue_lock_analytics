"""
Creates a dashboard login user.

Usage:
    python -m scripts.create_user
"""
import getpass
import os
import sqlite3

from app.auth import hash_password
from app.storage import StorageManager

DB_PATH = os.environ.get("TELEMETRY_DB_PATH", "telemetry_grid.db")


def main() -> None:
    db = StorageManager(db_path=DB_PATH)
    db.initialize_schema()

    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    try:
        db.create_user(username, hash_password(password))
        print(f"[OK] User '{username}' created.")
    except sqlite3.IntegrityError:
        print(f"[ERROR] Username '{username}' already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
