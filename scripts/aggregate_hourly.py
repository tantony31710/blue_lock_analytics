"""
Rolls up raw device_telemetry rows into hourly_device_summaries and
daily_exposure_logs. Run periodically (e.g. via cron) or manually:

    python -m scripts.aggregate_hourly
"""
import os
import sqlite3

DB_PATH = os.environ.get("TELEMETRY_DB_PATH", "telemetry_grid.db")


def run() -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            device_id,
            strftime('%Y-%m-%d %H:00:00', timestamp) as hourly_window,
            MAX(drift_index) as max_drift,
            SUM(CASE WHEN status = 'CRITICAL_ANOMALY' THEN 1 ELSE 0 END) as anomalies
        FROM device_telemetry
        GROUP BY device_id, hourly_window
        """
    )
    rows = cursor.fetchall()

    for device_id, window, max_drift, anomalies in rows:
        cursor.execute(
            """
            INSERT INTO hourly_device_summaries (device_id, hourly_window, peak_drift_index, anomaly_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(device_id, hourly_window) DO UPDATE SET
                peak_drift_index = excluded.peak_drift_index,
                anomaly_count = excluded.anomaly_count
            """,
            (device_id, window, max_drift, anomalies),
        )

        anomaly_minutes = anomalies / 60.0
        tracking_date = window.split(" ")[0]
        risk_rating = "CRITICAL" if anomaly_minutes > 5.0 else "MODERATE" if anomaly_minutes > 2.0 else "LOW"

        cursor.execute(
            """
            INSERT INTO daily_exposure_logs (device_id, tracking_date, total_anomaly_minutes, exposure_risk_rating)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(device_id, tracking_date) DO UPDATE SET
                total_anomaly_minutes = total_anomaly_minutes + excluded.total_anomaly_minutes,
                exposure_risk_rating = excluded.exposure_risk_rating
            """,
            (device_id, tracking_date, anomaly_minutes, risk_rating),
        )

    conn.commit()
    conn.close()
    return len(rows)


if __name__ == "__main__":
    count = run()
    print(f"[AGGREGATOR] Processed {count} device/hour buckets.")
