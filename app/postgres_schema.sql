-- =====================================================================
-- Blue Lock Analytics — Postgres schema (Supabase)
-- Converted from the original SQLite schema for deployment on Vercel,
-- where the filesystem is ephemeral and a real database is required.
-- =====================================================================

-- 0. Dashboard user accounts (JWT login)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 1. Raw ingested telemetry (one row per received frame)
CREATE TABLE IF NOT EXISTS device_telemetry (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    device_id TEXT NOT NULL,
    drift_index REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp
ON device_telemetry (device_id, "timestamp");

CREATE INDEX IF NOT EXISTS idx_telemetry_status
ON device_telemetry (status);

-- 2. Hourly rollups, built by scripts/aggregate_hourly.py
CREATE TABLE IF NOT EXISTS hourly_device_summaries (
    summary_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id TEXT NOT NULL,
    hourly_window TEXT NOT NULL,           -- 'YYYY-MM-DD HH:00:00'
    peak_drift_index REAL,
    anomaly_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (device_id, hourly_window)
);

CREATE INDEX IF NOT EXISTS idx_hourly_device_window
ON hourly_device_summaries (device_id, hourly_window);

-- 3. Cumulative daily anomaly exposure per device
CREATE TABLE IF NOT EXISTS daily_exposure_logs (
    log_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id TEXT NOT NULL,
    tracking_date DATE NOT NULL,
    total_anomaly_minutes REAL NOT NULL DEFAULT 0.0,
    exposure_risk_rating TEXT NOT NULL DEFAULT 'LOW',
    UNIQUE (device_id, tracking_date)
);

CREATE INDEX IF NOT EXISTS idx_exposure_device_date
ON daily_exposure_logs (device_id, tracking_date);

-- 4. Reporting views (read-only, used by the API layer)
CREATE OR REPLACE VIEW view_daily_device_health AS
SELECT device_id, tracking_date, total_anomaly_minutes, exposure_risk_rating
FROM daily_exposure_logs
ORDER BY tracking_date DESC, total_anomaly_minutes DESC;

CREATE OR REPLACE VIEW view_critical_risk_watchlist AS
SELECT device_id, tracking_date, total_anomaly_minutes, exposure_risk_rating
FROM daily_exposure_logs
WHERE exposure_risk_rating = 'CRITICAL'
ORDER BY total_anomaly_minutes DESC;

CREATE OR REPLACE VIEW view_hourly_drift_spikes AS
SELECT device_id, hourly_window, peak_drift_index, anomaly_count
FROM hourly_device_summaries
WHERE peak_drift_index > 4000.0
ORDER BY peak_drift_index DESC;
