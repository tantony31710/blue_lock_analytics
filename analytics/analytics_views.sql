-- =====================================================================
-- Module: views.sql
-- Description: Analytics Engineering layer defining virtual reporting views
--              for patient health dashboards and critical risk monitoring.
-- =====================================================================

-- 1. Daily Executive Health Summary
-- Aggregates total daily anomaly exposure and peak drift indices per device
CREATE VIEW IF NOT EXISTS view_daily_device_health AS
SELECT 
    device_id,
    tracking_date,
    total_anomaly_minutes,
    exposure_risk_rating
FROM environmental_exposure_logs
ORDER BY tracking_date DESC, total_anomaly_minutes DESC;

-- 2. Critical Risk Watchlist
-- Instantly filters devices that hit 'CRITICAL' exposure risk ratings
CREATE VIEW IF NOT EXISTS view_critical_risk_watchlist AS
SELECT 
    device_id,
    tracking_date,
    total_anomaly_minutes,
    exposure_risk_rating
FROM environmental_exposure_logs
WHERE exposure_risk_rating = 'CRITICAL'
ORDER BY total_anomaly_minutes DESC;

-- 3. Hourly Drift Spikes
-- Shows top peak drift indices recorded across all hourly windows
CREATE VIEW IF NOT EXISTS view_hourly_drift_spikes AS
SELECT 
    device_id,
    hourly_window,
    peak_drift_index,
    anomaly_count
FROM hourly_patient_summaries
WHERE peak_drift_index > 4000.0
ORDER BY peak_drift_index DESC;