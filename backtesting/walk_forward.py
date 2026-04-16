import pandas as pd
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger("WalkForwardOptimizer")

class WalkForwardOptimizer:
    def __init__(self, data: pd.DataFrame, train_window_size: int, test_window_size: int):
        """
        :param data: The entire dataset for the backtest. Must be sorted chronologically.
        :param train_window_size: Number of rows matching the training window (in-sample).
        :param test_window_size: Number of rows matching the testing window (out-of-sample).
        """
        self.data = data
        self.train_window_size = train_window_size
        self.test_window_size = test_window_size

    def run_optimization(self, 
                         train_func: Callable[[pd.DataFrame], Any], 
                         test_func: Callable[[Any, pd.DataFrame], Dict]) -> List[Dict]:
        """
        Executes the walk-forward optimization loop.
        :param train_func: Function that takes historical training rows and returns a trained model/strategy.
        :param test_func: Function that takes the trained model and testing rows, returning a performance metrics dict.
        :return: List of performance metrics per out-of-sample window test.
        """
        logger.info(f"Starting Walk-Forward Optimization (Train: {self.train_window_size}, Test: {self.test_window_size})")
        results = []
        
        total_rows = len(self.data)
        current_idx = 0
        
        window_count = 1
        while current_idx + self.train_window_size < total_rows:
            train_end_idx = current_idx + self.train_window_size
            test_end_idx = min(train_end_idx + self.test_window_size, total_rows)
            
            train_data = self.data.iloc[current_idx:train_end_idx]
            test_data = self.data.iloc[train_end_idx:test_end_idx]
            
            logger.debug(f"Window {window_count}: Train [{current_idx}:{train_end_idx}], Test [{train_end_idx}:{test_end_idx}]")
            
            # Train step (In-Sample)
            model = train_func(train_data)
            
            # Test step (Out-of-Sample)
            window_metrics = test_func(model, test_data)
            window_metrics['window'] = window_count
            window_metrics['train_start_idx'] = current_idx
            window_metrics['test_start_idx'] = train_end_idx
            
            results.append(window_metrics)
            
            # Slide the window forward by the testing window size
            # This ensures robust walk-forward validation (Train and Test roll forward synchronously)
            current_idx += self.test_window_size
            window_count += 1
            
        logger.info(f"Walk-Forward Optimization completed. Total Windows Evaluated: {window_count - 1}")
        return results
