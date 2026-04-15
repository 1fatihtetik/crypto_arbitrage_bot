import numpy as np
import logging
from typing import Dict, List
from shared.redis_client import RedisManager

logger = logging.getLogger("FeatureStore")

class FeatureStore:
    def __init__(self, redis_manager: RedisManager, window_size: int = 100):
        self.redis = redis_manager
        self.window_size = window_size
        
        # Local cache for blazing fast Z-score array computation before dumping to Redis
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}

    def ingest_book_update(self, exchange: str, best_bid: float, best_ask: float, volume: float):
        """Updates internal arrays, computes rolling statistics, and caches to Redis."""
        mid_price = (best_bid + best_ask) / 2.0
        
        if exchange not in self.price_history:
            self.price_history[exchange] = []
            self.volume_history[exchange] = []
            
        self.price_history[exchange].append(mid_price)
        self.volume_history[exchange].append(volume)
        
        # Truncate to window
        if len(self.price_history[exchange]) > self.window_size:
            self.price_history[exchange].pop(0)
            self.volume_history[exchange].pop(0)

    def get_vwap(self, exchange: str) -> float:
        """Calculates Volume Weighted Average Price using fast numpy."""
        if exchange not in self.price_history or len(self.price_history[exchange]) == 0:
            return 0.0
            
        prices = np.array(self.price_history[exchange], dtype=np.float32)
        vols = np.array(self.volume_history[exchange], dtype=np.float32)
        total_vol = np.sum(vols)
        
        if total_vol == 0:
            return prices[-1]
            
        return np.sum(prices * vols) / total_vol

    def get_price_zscore(self, exchange: str) -> float:
        """Calculates Z-Score of the current price relative to the rolling window."""
        if exchange not in self.price_history or len(self.price_history[exchange]) < 2:
            return 0.0
            
        prices = np.array(self.price_history[exchange], dtype=np.float32)
        current_price = prices[-1]
        mean = np.mean(prices)
        std = np.std(prices)
        
        if std == 0:
            return 0.0
            
        return (current_price - mean) / std

    def get_feature_vector(self, exchange: str) -> np.ndarray:
        """Returns a compiled feature vector for ML inference."""
        zscore = self.get_price_zscore(exchange)
        vwap = self.get_vwap(exchange)
        
        return np.array([[zscore, vwap]], dtype=np.float32)
