import numpy as np
import logging
from ml.model_registry import ModelRegistry

logger = logging.getLogger("SmartOrderRouter")

class SmartOrderRouter:
    """
    Simulates a Reinforcement Learning policy model for slicing or routing large block trades 
    across multiple liquidity venues to minimize market impact.
    """
    def __init__(self, model_registry: ModelRegistry):
        self.registry = model_registry

    def determine_optimal_route(self, spread: float, volume: float, capital_allocated: float, exchange_latency: float) -> list:
        """
        Infers the action from the ONNX RL Model.
        Returns a mock dictionary of allocations per exchange.
        """
        rl_state = np.array([[spread, volume, capital_allocated, exchange_latency]], dtype=np.float32)
        action_output = self.registry.predict("routing_policy", rl_state)
        
        # E.g. Action space predicts % allocations for Binance vs Kraken
        if action_output is not None:
            # Normalize the mock raw neural net outputs into percentages summing to 1.0
            raw_action = action_output[0]
            raw_action = np.maximum(raw_action, 0.01) # Prevent negative or zero
            allocations = raw_action / np.sum(raw_action)
            return {"binance_pct": allocations[0], "kraken_pct": allocations[1]}
        
        # Fallback to naive routing if ML is offline
        return {"binance_pct": 0.5, "kraken_pct": 0.5}
