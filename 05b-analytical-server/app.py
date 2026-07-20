"""
Module: app.py
Description: Lightweight analytical Flask microservice exposing virtual database
             views as RESTful JSON endpoints.
"""
import os
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# Add this right after creating `app = Flask(__name__)` inside app.py:
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Locate the database file at the workspace root
ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_WORKSPACE, "telemetry_grid.db")

def query_view(view_name):
    """Helper function to cleanly fetch all records from an internal view."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {view_name}")
        
        # Extract column headers dynamically
        columns = [desc[0] for desc in cursor.description]
        
        # Format rows into readable key-value objects
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results, None
    except Exception as err:
        return None, str(err)
    finally:
        conn.close()

@app.route("/api/analytics/daily-health", methods=["GET"])
def get_daily_health():
    data, error = query_view("view_daily_device_health")
    if error:
        return jsonify({"status": "error", "message": error}), 500
    return jsonify({"status": "success", "data": data})

@app.route("/api/analytics/watchlist", methods=["GET"])
def get_watchlist():
    data, error = query_view("view_critical_risk_watchlist")
    if error:
        return jsonify({"status": "error", "message": error}), 500
    return jsonify({"status": "success", "data": data})

@app.route("/api/analytics/drift-spikes", methods=["GET"])
def get_drift_spikes():
    data, error = query_view("view_hourly_drift_spikes")
    if error:
        return jsonify({"status": "error", "message": error}), 500
    return jsonify({"status": "success", "data": data})

if __name__ == "__main__":
    print("[SERVER] Spinning up Analytics Engine REST Service...")
    app.run(host="127.0.0.1", port=5001, debug=True)