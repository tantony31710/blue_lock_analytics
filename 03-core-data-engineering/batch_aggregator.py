"""
Module: batch_aggregator.py
Description: Data engineering batch processor configured specifically for 
             the actual columns in 'device_telemetry'.
"""
import os
import sys
import sqlite3

ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_hourly_aggregation():
    print("[DATA ENGINEER] Initializing batch aggregation run...")
    
    db_path = os.path.join(ROOT_WORKSPACE, "telemetry_grid.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Query targeting only columns that actually exist in device_telemetry
        query = """
            SELECT 
                device_id,
                strftime('%Y-%m-%d %H:00:00', timestamp) as hourly_window,
                MAX(drift_index) as max_drift,
                SUM(CASE WHEN status = 'CRITICAL_ANOMALY' THEN 1 ELSE 0 END) as anomalies
            FROM device_telemetry
            GROUP BY device_id, hourly_window
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            device_id, window, max_drift, anomalies = row
            
            # Upsert into hourly_patient_summaries
            cursor.execute("""
                INSERT INTO hourly_patient_summaries 
                    (device_id, hourly_window, peak_drift_index, anomaly_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(device_id, hourly_window) DO UPDATE SET
                    peak_drift_index = excluded.peak_drift_index,
                    anomaly_count = excluded.anomaly_count
            """, (device_id, window, max_drift, anomalies))
            
            # Calculate cumulative exposure window (assuming 1-second transmission loops)
            anomaly_minutes = (anomalies * 1.0) / 60.0
            tracking_date = window.split(" ")[0] if window else "UNKNOWN"
            
            risk_rating = "LOW"
            if anomaly_minutes > 5.0:
                risk_rating = "CRITICAL"
            elif anomaly_minutes > 2.0:
                risk_rating = "MODERATE"
                
            cursor.execute("""
                INSERT INTO environmental_exposure_logs (device_id, tracking_date, total_anomaly_minutes, exposure_risk_rating)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(device_id, tracking_date) DO UPDATE SET
                    total_anomaly_minutes = total_anomaly_minutes + excluded.total_anomaly_minutes,
                    exposure_risk_rating = ?
            """, (device_id, tracking_date, anomaly_minutes, risk_rating, risk_rating))
            
        conn.commit()
        print(f"[DATA ENGINEER] Success! Processed {len(rows)} data aggregation blocks cleanly.")
        
    except Exception as err:
        print(f"[DATA ENGINEER ERROR] Failed to execute batch aggregation: {err}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_hourly_aggregation()