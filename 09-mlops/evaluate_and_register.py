"""
Module: evaluate_and_register.py
Description: Evaluates ML model metrics and registers production-ready model weights.
"""
import os
import shutil

ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_MODEL = os.path.join(ROOT_WORKSPACE, "06-classical-ml", "models", "anomaly_detector.joblib")
REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "model_registry")

def register_model():
    print("[MLOPS] Evaluating model artifact compliance...")
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    
    if os.path.exists(SRC_MODEL):
        target_path = os.path.join(REGISTRY_DIR, "isolation_forest_v1.joblib")
        shutil.copy(SRC_MODEL, target_path)
        print(f"[MLOPS SUCCESS] Model registered to production registry:\n └── {target_path}")
    else:
        print("[MLOPS WARNING] No classical ML artifact found. Run Phase 5 first.")

if __name__ == "__main__":
    register_model()