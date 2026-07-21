"""
Core anomaly-scoring math for telemetry vectors.

Given a live metric vector (e.g. [engine_temp, rpm, vibration_amplitude])
and a healthy baseline vector of the same shape, calculate_vector_drift
returns the Euclidean distance between them. Larger distance = further
from "normal" behavior.
"""
from typing import List, Dict, Any


def calculate_vector_drift(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Euclidean distance between two equal-length numeric vectors:
        d = sqrt(sum((a_i - b_i)^2))

    Raises ValueError if the vectors don't have the same length —
    a mismatch here almost always means malformed input upstream,
    so we fail loudly rather than silently truncating/padding.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            f"Vector length mismatch: {len(vector_a)} vs {len(vector_b)}"
        )

    return sum((a - b) ** 2 for a, b in zip(vector_a, vector_b)) ** 0.5


class TelemetryValidator:
    """
    Wraps calculate_vector_drift with a baseline and a critical threshold,
    so callers just pass in a device's live metrics and get back a
    classification instead of a raw number.
    """

    def __init__(self, baseline_metrics: List[float], critical_threshold: float):
        self.baseline = baseline_metrics
        self.threshold = critical_threshold

    def process_stream_frame(self, device_id: str, current_metrics: List[float]) -> Dict[str, Any]:
        try:
            drift_index = calculate_vector_drift(current_metrics, self.baseline)
            status = "CRITICAL_ANOMALY" if drift_index > self.threshold else "HEALTHY"
            return {
                "device_id": device_id,
                "drift_index": round(drift_index, 4),
                "status": status,
            }
        except ValueError as err:
            return {
                "device_id": device_id,
                "status": "INVALID",
                "error": str(err),
            }
