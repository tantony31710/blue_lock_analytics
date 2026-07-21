"""
<<<<<<< HEAD
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
=======
Module: train_anomaly_detector.py
Description: Trains an Isolation Forest model on historical telemetry logs
             to detect complex, multi-variable anomalies dynamically.
"""
import os
import sqlite3
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_WORKSPACE, "telemetry_grid.db")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def train_model():
    print("[ML PIPELINE] Fetching feature datasets from telemetry database...")
    
    conn = sqlite3.connect(DB_PATH)
    # Extract historical numerical metrics for pattern analysis
    query = "SELECT drift_index FROM device_telemetry"
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"[ML PIPELINE] Successfully loaded {len(df):,} metric records for training.")

    # Train Isolation Forest for Anomaly Detection
    print("[ML PIPELINE] Fitting Isolation Forest model...")
    model = IsolationForest(contamination=0.15, random_state=42)
    model.fit(df[['drift_index']])

    # Ensure model export directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "anomaly_detector.joblib")
    
    # Save the trained model artifact
    joblib.dump(model, model_path)
    print(f"[ML PIPELINE] Model successfully compiled and saved to:\n └── {model_path}")

if __name__ == "__main__":
    train_model()
>>>>>>> 03bb09388a7358a79f7e23d2506e3e1b2433c892
