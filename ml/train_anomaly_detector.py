"""
Trains an Isolation Forest on historical drift_index values to flag
anomalies statistically instead of via a fixed threshold.

Usage:
    python -m ml.train_anomaly_detector
"""
import os

import joblib
import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest

DB_PATH = os.environ.get("TELEMETRY_DB_PATH", "telemetry_grid.db")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_detector.joblib")


def train() -> str:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT drift_index FROM device_telemetry", conn)
    conn.close()

    if df.empty:
        raise RuntimeError("No telemetry rows found — run the client/mock generator first.")

    model = IsolationForest(contamination=0.15, random_state=42)
    model.fit(df[["drift_index"]])

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return MODEL_PATH


if __name__ == "__main__":
    print(f"[ML] Training on {DB_PATH} ...")
    path = train()
    print(f"[ML] Model saved to {path}")
