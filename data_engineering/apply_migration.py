"""
Temporary script to apply SQL migrations using Python's built-in sqlite3 module.
"""
import sqlite3
import os

db_path = "telemetry_grid.db"
sql_file_path = "05-analytics-engineering/analytics_views.sql"

if not os.path.exists(sql_file_path):
    print(f"[ERROR] Could not find schema file at: {sql_file_path}")
    exit(1)

print(f"[MIGRATION] Opening connection to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print(f"[MIGRATION] Reading schema definitions from {sql_file_path}...")
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    print("[MIGRATION] Executing schema script...")
    cursor.executescript(sql_script)
    conn.commit()
    print("[MIGRATION] Success! Tables and indexes compiled successfully.")
    
except Exception as e:
    print(f"[MIGRATION ERROR] Failed to apply schema: {e}")
    conn.rollback()
finally:
    conn.close()