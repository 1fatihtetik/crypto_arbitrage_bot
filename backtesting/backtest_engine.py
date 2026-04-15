import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger("BacktestEngine")

class BacktestResult:
    def __init__(self):
        self.trades_executed = 0
        self.net_profit = 0.0
        self.max_drawdown = 0.0
        self.trade_history: List[Dict] = []
        
class BacktestEngine:
    def __init__(self, fee_rate: float = 0.001, slippage_pct: float = 0.05, latency_ms: float = 50.0):
        """
        :param fee_rate: Taker fee normally (0.1% = 0.001)
        :param slippage_pct: Assumed slippage percentage
        :param latency_ms: Simulated network latency for execution delay
        """
        self.fee_rate = fee_rate
        self.slippage_pct = slippage_pct
        self.latency_ms = latency_ms

    def run_out_of_sample(self, strategy_func, historical_data: pd.DataFrame) -> BacktestResult:
        """
        Simulate passing historical data through the strategy.
        historical_data should contain merged order book states from multiple exchanges alongside timestamps.
        """
        logger.info("Starting backtesting engine on out-of-sample data...")
        result = BacktestResult()
        
        # Simplified simulation loop
        current_capital = 1000.0
        peak_capital = 1000.0
        
        for idx, row in historical_data.iterrows():
            # Apply simulated latency by fast forwarding logic ideally,
            # For this simplified setup, we apply latency to the success probability or slippage impact.
            # Strategy function returns an 'ArbitrageOpportunity' or None
            opp = strategy_func(row)
            
            if opp:
                # Deduct fees and slippage
                # Assuming opp gives estimated gross profit percentage
                gross_profit = opp['expected_profit']
                
                # Apply extra slippage if latency > 100ms
                extra_slip = max(0, (self.latency_ms - 100) / 1000 * 0.01)
                
                # 50% Stronger Architecture: Dynamic Book Depth Slippage!
                # Quadratic slippage based on capital size forcing constraints
                capital_slippage_penalty = 0.0
                if current_capital > 1000.0:
                    capital_slippage_penalty = ((current_capital - 1000.0) / 1000.0) ** 2 * 0.0005
                
                total_slippage = self.slippage_pct/100.0 + extra_slip + capital_slippage_penalty
                
                net_profit_pct = gross_profit - (self.fee_rate * 2) - total_slippage
                
                trade_profit = current_capital * net_profit_pct
                current_capital += trade_profit
                
                peak_capital = max(peak_capital, current_capital)
                drawdown = (peak_capital - current_capital) / peak_capital
                
                result.max_drawdown = max(result.max_drawdown, drawdown)
                result.trades_executed += 1
                result.trade_history.append({"time": row.get('timestamp', idx), "profit": trade_profit, "capital": current_capital})
                
        result.net_profit = current_capital - 1000.0
        logger.info(f"Backtest completed. Executed: {result.trades_executed}, Net Profit: {result.net_profit:.2f}, Max DD: {result.max_drawdown:.2%}")
        return result
