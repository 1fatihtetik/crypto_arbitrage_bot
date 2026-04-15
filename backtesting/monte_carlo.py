import random
import logging
from typing import List

logger = logging.getLogger("MonteCarlo")

class MonteCarloSimulator:
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations

    def run_simulation(self, trade_results: List[float], initial_capital: float = 1000.0) -> dict:
        """
        Runs Monte Carlo simulation by shuffling historical trade results.
        :param trade_results: List of percentage returns from historical backtests (e.g. 0.01 for 1% win, -0.005 for 0.5% loss)
        :param initial_capital: Starting capital
        :return: Dict containing probability of ruin and average max drawdown.
        """
        if not trade_results:
            logger.warning("No trade results provided for Monte Carlo simulation.")
            return {"prob_ruin": 0.0, "avg_max_drawdown": 0.0}

        ruined_count = 0
        total_max_drawdown = 0.0
        ruin_threshold = initial_capital * 0.1  # Consider "ruin" if capital drops below 10% of initial

        for _ in range(self.iterations):
            capital = initial_capital
            peak_capital = initial_capital
            max_dd = 0.0
            
            # Shuffle the sequence of trade returns
            shuffled_trades = trade_results.copy()
            random.shuffle(shuffled_trades)
            
            ruined = False
            for trade_return in shuffled_trades:
                capital += (capital * trade_return)
                peak_capital = max(peak_capital, capital)
                
                if peak_capital > 0:
                    drawdown = (peak_capital - capital) / peak_capital
                    max_dd = max(max_dd, drawdown)
                
                if capital <= ruin_threshold:
                    ruined = True
                    break
            
            if ruined:
                ruined_count += 1
            total_max_drawdown += max_dd

        prob_ruin = ruined_count / self.iterations
        avg_max_drawdown = total_max_drawdown / self.iterations
        
        logger.info(f"Monte Carlo ({self.iterations} iters) - Prob of Ruin: {prob_ruin:.2%}, Avg Max DD: {avg_max_drawdown:.2%}")
        return {
            "prob_ruin": prob_ruin,
            "avg_max_drawdown": avg_max_drawdown
        }
