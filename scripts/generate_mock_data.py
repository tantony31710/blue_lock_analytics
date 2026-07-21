"""
Injects historical mock telemetry rows directly into the database for
scale/performance testing, bypassing the network layer.

Usage:
    python -m scripts.generate_mock_data --rows 200000
"""
import argparse
import random
import time

from app.db import adapt_query, get_connection

DEVICE_IDS = ["DEV-ALPHA", "DEV-BRAVO", "DEV-CHARLIE", "DEV-DELTA", "DEV-ECHO"]


def generate(target_rows: int, batch_size: int = 25000) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    base_time = time.time() - (30 * 24 * 60 * 60)  # 30 days back

    insert_query = adapt_query(
        "INSERT INTO device_telemetry (timestamp, device_id, drift_index, status) VALUES (?, ?, ?, ?)"
    )

    batch = []
    for i in range(target_rows):
        record_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(base_time + i * 12))
        drift = round(random.uniform(0.0, 6000.0), 4)
        status = "CRITICAL_ANOMALY" if drift > 50.0 else "HEALTHY"
        batch.append((record_time, random.choice(DEVICE_IDS), drift, status))

        if len(batch) >= batch_size:
            cursor.executemany(insert_query, batch)
            conn.commit()
            print(f"[MOCK DATA] {i + 1:,}/{target_rows:,} rows written")
            batch = []

    if batch:
        cursor.executemany(insert_query, batch)
        conn.commit()

    print("[MOCK DATA] Done.")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=50000)
    args = parser.parse_args()
    generate(args.rows)
