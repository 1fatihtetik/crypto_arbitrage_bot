import numpy as np
import logging
from ml.model_registry import ModelRegistry

logger = logging.getLogger("SafetyGate")

class MLSafetyGate:
    def __init__(self, model_registry: ModelRegistry):
        self.registry = model_registry

    def evaluate_trade(self, exchange: str, spread: float, expected_gross: float, order_size: float, recent_volume: float, toxicity_features: list) -> bool:
        """
        Runs the ONNX predictive layer.
        Returns True if the trade is SAFE to execute. 
        Returns False if the trade shouldn't be executed (e.g., highly toxic or slippage negates profit).
        """
        # 1. Tóxicity & Sniping Detector
        # Model expects: [trade_velocity, spread_volatility, whale_count]
        tox_array = np.array([toxicity_features], dtype=np.float32)
        tox_score = self.registry.predict("toxicity", tox_array)
        
        # Isolation Forest typically returns -1 for anomalies (toxic), 1 for normal
        if tox_score is not None and tox_score[0] == -1:
            logger.warning(f"Safety Gate blocked trade on {exchange}: High Toxicity Flow Detected!")
            return False

        # 2. Slippage & Impact Predictor
        # Model expects: [book_depth, recent_volume, order_size]
        # In a real environment, `book_depth` would be dynamically fetched from the FeatureStore
        book_depth = 50000.0 
        slip_array = np.array([[book_depth, recent_volume, order_size]], dtype=np.float32)
        predicted_slippage = self.registry.predict("slippage", slip_array)
        
        if predicted_slippage is not None:
            # We assume our mocked slippage regressor returns an absolute slippage value
            slippage_val = predicted_slippage[0]
            net_prediction = expected_gross - slippage_val
            if net_prediction <= 0:
                logger.warning(f"Safety Gate blocked trade on {exchange}: Predicted slippage ({slippage_val:.2f}) destroys expected profit ({expected_gross:.2f}).")
                return False

        # 3. Probability of Convergence Filter
        # Note: Added for holistic completeness, checks if prices will converge
        # expects: [rsi_divergence, order_flow_imbalance]
        conv_array = np.array([[30.5, 0.2]], dtype=np.float32) # Dummy features representing RSI and OFI
        convergence_prob = self.registry.predict("convergence", conv_array)
        
        # Assume class 1 means "will converge"
        if convergence_prob is not None and convergence_prob[0] == 0:
            logger.warning(f"Safety Gate blocked trade on {exchange}: Low probability of price convergence.")
            return False

        return True
