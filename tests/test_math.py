import os
import sys

# Setup root path for imports
ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_WORKSPACE not in sys.path:
    sys.path.insert(0, ROOT_WORKSPACE)

from telemetry_gateway.math_and_stats.Math import calculate_vector_drift

def test_calculate_vector_drift_perfect_match():
    """Test that identical vectors result in zero drift."""
    current = [10.0, 20.0, 30.0]
    baseline = [10.0, 20.0, 30.0]
    drift = calculate_vector_drift(current, baseline)
    assert drift == 0.0

def test_calculate_vector_drift_variation():
    """Test that different vectors result in positive drift."""
    current = [15.0, 25.0, 35.0]
    baseline = [10.0, 20.0, 30.0]
    drift = calculate_vector_drift(current, baseline)
    assert drift > 0.0

def test_calculate_vector_drift_types():
    """Test that the function handles float inputs correctly."""
    current = [10.5, 20.5, 30.5]
    baseline = [10.0, 20.0, 30.0]
    drift = calculate_vector_drift(current, baseline)
    assert isinstance(drift, float)
