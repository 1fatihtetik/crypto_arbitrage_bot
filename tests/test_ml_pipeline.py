import time
import numpy as np
import pytest
from ml.model_registry import ModelRegistry
from ml.safety_gate import MLSafetyGate

def test_onnx_inference_latency():
    """
    Validates that the entire safety gate containing Multiple ML models (Random Forest, XGBoost-Mock, IsolationForest)
    executes well under the 2ms requirement.
    """
    registry = ModelRegistry()
    
    # Check if models were generated properly by our setup script
    if "slippage" not in registry.sessions:
        pytest.skip("Models not generated. Run python scripts/generate_models.py first.")
        
    safety_gate = MLSafetyGate(registry)
    
    # Warm up pass (to avoid initial C++ cold start penalties in ONNX Runtime measuring)
    safety_gate.evaluate_trade("binance", 5.0, 10.0, 2.5, 100.0, [10.5, 2.1, 5])
    
    start_time = time.perf_counter()
    
    # The actual measured hot-path ML pipeline
    res = safety_gate.evaluate_trade("binance", 5.0, 10.0, 2.5, 100.0, [10.5, 2.1, 5])
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    # Verify strict latency bounds
    assert latency_ms < 2.0, f"ML Inference took too long: {latency_ms:.3f}ms (must be < 2ms)"
    assert res is not None
