from backtesting.backtest_engine import BacktestEngine
from backtesting.monte_carlo import MonteCarloSimulator

def mock_strategy_gross(row):
    """A mock strategy that always finds a 1% gross profit arbitrage"""
    return {"expected_profit": 0.01}

def test_backtest_engine_deducts_fees_and_slippage(historic_backtest_data):
    # Setup high fee (0.005) and high slippage (0.1% / 0.001)
    engine = BacktestEngine(fee_rate=0.005, slippage_pct=0.1, latency_ms=50.0)
    result = engine.run_out_of_sample(mock_strategy_gross, historic_backtest_data)
    
    # Gross profit is 0.01 (1%)
    # Total fees = 2 * 0.005 = 0.01
    # Slippage = 0.1 / 100 = 0.001
    # Net profit per trade = 0.01 - 0.01 - 0.001 = -0.001 (-0.1%)
    # Initial capital is 1000. 10 trades of -0.1%.
    # Should be negative net profit!
    assert result.trades_executed == 10
    assert result.net_profit < 0.0
    assert result.max_drawdown > 0.0

def test_backtest_engine_high_latency_penalty(historic_backtest_data):
    # Add severe latency of 500ms which incurs extra slippage penalty
    engine = BacktestEngine(fee_rate=0.001, slippage_pct=0.05, latency_ms=500.0)
    result = engine.run_out_of_sample(mock_strategy_gross, historic_backtest_data)
    
    # 500ms > 100ms. Penalty is (500-100)/1000 * 0.01 = 0.004 extra slippage
    # Gross = 0.01. normal fees = 2*0.001=0.002. fixed slip = 0.0005. 
    # Net should be 0.01 - 0.002 - 0.0005 - 0.004 = 0.0035 per trade (>0)
    assert result.trades_executed == 10
    assert result.net_profit > 0.0
    
def test_monte_carlo_probability_bounds():
    simulator = MonteCarloSimulator(iterations=10000)
    # Trade results: 50% chance to win 2%, 50% chance to lose 2.5%
    # This is slightly negative expectancy, so probability of ruin should be >0
    historic_trades = [0.02, 0.02, 0.02, 0.02, 0.02, -0.025, -0.025, -0.025, -0.025, -0.025] * 10
    
    metrics = simulator.run_simulation(historic_trades, initial_capital=1000.0)
    
    assert 0.0 <= metrics['prob_ruin'] <= 1.0
    assert metrics['avg_max_drawdown'] > 0.0

def test_monte_carlo_infinite_wealth():
    simulator = MonteCarloSimulator(iterations=10000)
    # Always makes money, no ruin
    always_win = [0.05] * 50
    metrics = simulator.run_simulation(always_win, initial_capital=1000.0)
    assert metrics['prob_ruin'] == 0.0
    assert metrics['avg_max_drawdown'] == 0.0
