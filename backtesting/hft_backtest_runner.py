import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("HFTBacktest")

class HFTBacktestRunner:
    """
    A Pandas-based simulation matrix estimating order fills based on depth and spreads.
    Designed as a native fallback since hftbacktest binaries frequently encounter Numba/Rust version 
    mismatches on Windows architectures.
    """
    def __init__(self, data_feed: pd.DataFrame, simulated_latency_ms: float = 50.0):
        self.data_feed = data_feed
        self.latency_ms = simulated_latency_ms
        
    def calculate_execution_slip(self, order_size_usd: float) -> pd.DataFrame:
        """
        Simulates parsing through historical arrays and calculates the geometric
        execution slip (difference between predicted target price & real fill).
        """
        results = []
        
        for idx, row in self.data_feed.iterrows():
            # For this simulation, we mock the bid/ask depths
            # In a real parquet replay, these would be precise floats parsed from L2 snaps
            best_bid = row['price'] - np.random.uniform(0.1, 1.0)
            best_ask = row['price'] + np.random.uniform(0.1, 1.0)
            
            # Predict we can hit the best_ask
            predicted_price = best_ask
            
            # Simulate 50ms latency impacting the orderbook before we arrive
            # Network latency creates spread widening
            latency_spread_impact = np.random.normal(loc=(self.latency_ms / 1000.0) * 0.5, scale=0.1)
            latency_spread_impact = max(0.0, latency_spread_impact)
            
            # Simulate Volume depth slippage 
            volume_penalty = (order_size_usd / 10000.0) * np.random.uniform(0.1, 0.5)
            
            realized_fill = best_ask + latency_spread_impact + volume_penalty
            execution_slip = realized_fill - predicted_price
            
            # Record probability
            fill_probability = 1.0 if realized_fill <= predicted_price else max(0.0, 1.0 - (execution_slip / 2.0))
            
            results.append({
                "timestamp": row['timestamp'],
                "predicted_price": predicted_price,
                "realized_price": realized_fill,
                "execution_slip": execution_slip,
                "fill_probability": fill_probability
            })
            
        return pd.DataFrame(results)
