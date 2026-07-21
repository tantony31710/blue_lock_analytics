-- =====================================================================
-- Module: optimized_indexing.sql
-- Description: Composite indexing strategy for high-frequency queries 
--              on the device_telemetry table.
-- =====================================================================

-- 1. Accelerates filtering by device over time ranges
CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp 
ON device_telemetry (device_id, timestamp);

-- 2. Accelerates rapid filtering for critical anomaly detection
CREATE INDEX IF NOT EXISTS idx_telemetry_status 
ON device_telemetry (status);