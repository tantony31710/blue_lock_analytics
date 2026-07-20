-- =====================================================================
-- Module: migration_summary.sql
-- Description: Time-series aggregation tables matching the actual 
--              'device_telemetry' table schema.
-- =====================================================================
DROP TABLE IF EXISTS hourly_patient_summaries;
DROP TABLE IF EXISTS environmental_exposure_logs;
-- 1. Table for tracking hourly aggregated patient/device metrics
CREATE TABLE IF NOT EXISTS hourly_patient_summaries (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    hourly_window TEXT NOT NULL,          -- Format: YYYY-MM-DD HH:00:00
    avg_engine_temp REAL DEFAULT 0.0,                 
    avg_rpm INTEGER DEFAULT 0,                      
    avg_vibration REAL DEFAULT 0.0,                  
    peak_drift_index REAL,                
    anomaly_count INTEGER DEFAULT 0,      
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, hourly_window)      -- Prevents duplicate windows on multiple runs
);

-- 2. Table for tracking cumulative environmental exposure windows
CREATE TABLE IF NOT EXISTS environmental_exposure_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    tracking_date DATE NOT NULL,
    total_anomaly_minutes REAL DEFAULT 0.0,
    exposure_risk_rating TEXT DEFAULT 'LOW',
    UNIQUE(device_id, tracking_date)
);

-- 3. Optimization Indexes for rapid batch time lookups
CREATE INDEX IF NOT EXISTS idx_hourly_device_window 
ON hourly_patient_summaries (device_id, hourly_window);

CREATE INDEX IF NOT EXISTS idx_exposure_device_date 
ON environmental_exposure_logs (device_id, tracking_date);