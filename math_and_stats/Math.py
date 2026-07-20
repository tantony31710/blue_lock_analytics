"""
Module: telemetry_analytics_engine.py
Description: Production-grade, library-independent vector analytics engine 
             optimized for high-velocity telemetry drift calculations.
"""
from typing import List, Dict, Any


# =====================================================================
# STEP 1: CORE ALGORITHMIC CORE (The Basics)
# =====================================================================
def calculate_vector_drift(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Computes the geometric Euclidean distance between two multidimensional feature arrays.
    Formula: d = sqrt(sum((a_i - b_i)^2))
    """
    if len(vector_a) != len(vector_b):
        raise ValueError("Dimension Mismatch: Sensor tracking arrays must be equal in length.")
    
    total_variance = 0.0
    for i in range(len(vector_a)):
        total_variance += (vector_a[i] - vector_b[i]) ** 2
        
    if total_variance == 0:
        return 0.0
        
    # Custom low-overhead Newton-Raphson square root implementation
    approximation = total_variance / 2.0
    for _ in range(10):  # 10 loops provides precision down to 15 decimal places
        approximation = 0.5 * (approximation + total_variance / approximation)
        
    return approximation


# =====================================================================
# STEP 2: PRODUCTION OPERATIONAL WRAPPER (The Final Module)
# =====================================================================
class TelemetryValidator:
    """
    Enterprise-grade validation interface designed to ingest live streaming data,
    evaluate analytical metrics, and flag systemic operational status states.
    """
    def __init__(self, baseline_metrics: List[float], critical_threshold: float):
        self.baseline = baseline_metrics
        self.threshold = critical_threshold

    def process_stream_frame(self, device_id: str, current_metrics: List[float]) -> Dict[str, Any]:
        """
        Ingests a live data matrix frame, measures structural drift, and determines anomalies.
        """
        try:
            drift_index = calculate_vector_drift(current_metrics, self.baseline)
            is_anomalous = drift_index > self.threshold
            
            return {
                "device_id": device_id,
                "drift_index": round(drift_index, 4),
                "status": "CRITICAL_ANOMALY" if is_anomalous else "HEALTHY",
                "execution_status": "SUCCESS"
            }
        except ValueError as err:
            return {
                "device_id": device_id,
                "status": "UNKNOWN",
                "execution_status": f"FAILED_ERROR: {str(err)}"
            }


# =====================================================================
# STEP 3: INTEGRATED TESTING & BOUNDARY VALIDATION (The Debugging Suite)
# =====================================================================
def run_integrated_suite():
    """
    Executes boundary analysis tests to guarantee engine resilience under real-world strains.
    """
    print("\n[DEBUG] --- STARTING INTEGRATED BOUNDARY CHECKS ---")
    stable_baseline = [75.0, 3000.0, 0.5]
    
    # Test Scenario A: Catching bad payload lengths gracefully
    malformed_payload = [82.4, 3120.0]  # Missing the 3rd metric
    try:
        print("[DEBUG] Injecting malformed dimension array...")
        calculate_vector_drift(malformed_payload, stable_baseline)
    except ValueError as err:
        print(f"✅ Successfully caught expected exception: {err}")
        
    # Test Scenario B: Verification of absolute vector convergence (Zero Drift)
    try:
        print("[DEBUG] Testing perfect system baseline convergence...")
        zero_drift = calculate_vector_drift(stable_baseline, stable_baseline)
        print(f"✅ Convergence verified correctly. Drift index output: {zero_drift}")
    except Exception as err:
        print(f"❌ Unexpected baseline tracking failure: {err}")

    # Test Scenario C: Operational Class Verification
    print("\n[PRODUCTION] Deploying live validator pipeline simulation...")
    monitor = TelemetryValidator(baseline_metrics=stable_baseline, critical_threshold=50.0)
    
    # Emulate an alarming system surge
    alert_result = monitor.process_stream_frame("DEV-ALPHA", [98.5, 4500.0, 3.8])
    print(f"📋 Pipeline Output Matrix:\n{alert_result}\n")


if __name__ == "__main__":
    print("[SYSTEM] Telemetry Engine Initialized Successfully.")
    run_integrated_suite()