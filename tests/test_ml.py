import os
import joblib
import pytest
from sklearn.ensemble import IsolationForest

def test_model_artifact_exists():
    """Verify that the trained model file exists in the expected directory."""
    model_path = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "anomaly_detector.joblib")
    assert os.path.exists(model_path), "ML model artifact not found. Run training script first."

def test_model_loading_and_prediction():
    """Verify that the model can be loaded and perform basic predictions."""
    model_path = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "anomaly_detector.joblib")
    if not os.path.exists(model_path):
        pytest.skip("Model artifact missing, skipping prediction test.")
    
    model = joblib.load(model_path)
    assert isinstance(model, IsolationForest)
    
    # Test prediction with a mock data point
    # Isolation Forest returns 1 for inliers, -1 for outliers
    prediction = model.predict([[50.0]])
    assert prediction[0] in [1, -1]
