import pytest

from app.math_engine import calculate_vector_drift, TelemetryValidator


def test_zero_drift_for_identical_vectors():
    assert calculate_vector_drift([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 0.0


def test_known_distance():
    # 3-4-5 right triangle in 2D -> distance should be exactly 5
    assert calculate_vector_drift([0.0, 0.0], [3.0, 4.0]) == 5.0


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        calculate_vector_drift([1.0, 2.0], [1.0, 2.0, 3.0])


def test_validator_flags_healthy_reading():
    validator = TelemetryValidator(baseline_metrics=[75.0, 3000.0, 0.5], critical_threshold=50.0)
    result = validator.process_stream_frame("DEV-TEST", [75.5, 3010.0, 0.6])
    assert result["status"] == "HEALTHY"


def test_validator_flags_critical_reading():
    validator = TelemetryValidator(baseline_metrics=[75.0, 3000.0, 0.5], critical_threshold=50.0)
    result = validator.process_stream_frame("DEV-TEST", [110.0, 6500.0, 3.0])
    assert result["status"] == "CRITICAL_ANOMALY"


def test_validator_handles_bad_input_gracefully():
    validator = TelemetryValidator(baseline_metrics=[75.0, 3000.0, 0.5], critical_threshold=50.0)
    result = validator.process_stream_frame("DEV-TEST", [75.0, 3000.0])  # missing a dimension
    assert result["status"] == "INVALID"
    assert "error" in result
