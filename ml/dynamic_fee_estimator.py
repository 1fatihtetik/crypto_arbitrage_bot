import numpy as np
import logging
from ml.model_registry import ModelRegistry

logger = logging.getLogger("DynamicFeeEstimator")

class DynamicFeeEstimator:
    """
    Uses Linear Regression to dynamically estimate transaction fees based on mempool and network congestion.
    """
    def __init__(self, model_registry: ModelRegistry):
        self.registry = model_registry

    def estimate_fee(self, network_congestion: float, mempool_size: float, blocks_empty: float) -> float:
        """
        Outputs the estimated transaction fee value directly via ONNX linear regression prediction.
        """
        features = np.array([[network_congestion, mempool_size, blocks_empty]], dtype=np.float32)
        predicted_fee = self.registry.predict("fee_estimator", features)
        
        if predicted_fee is not None:
            # Linear Regression outputs an exact numerical value for fee estimation
            return float(predicted_fee[0])
            
        # Fallback to static fee if ML engine fails or model is missing
        return 0.001
