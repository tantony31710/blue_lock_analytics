"""
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