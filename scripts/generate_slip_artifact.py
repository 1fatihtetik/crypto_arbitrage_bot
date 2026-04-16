import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from backtesting.hft_backtest_runner import HFTBacktestRunner

def main():
    print("Generating HFT Execution Slip Analysis...")
    
    # 1. Generate Fake Replay Data (normally loaded from the .parquet sink)
    dates = pd.date_range("2026-04-16", periods=1000, freq='s')
    data = pd.DataFrame({
        'timestamp': dates,
        'price': 60000.0 + np.cumsum(np.random.normal(0, 10, 1000))
    })
    
    # 2. Run simulation engine
    runner = HFTBacktestRunner(data_feed=data, simulated_latency_ms=50.0)
    # Simulating a highly aggressive $20,000 order block
    results_df = runner.calculate_execution_slip(order_size_usd=20000.0)
    
    # 3. Render and save visualization artifact
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Histogram of slippage distributions
    ax1.hist(results_df['execution_slip'], bins=50, color='crimson', alpha=0.7)
    ax1.set_title("HFT Simulation: Execution Slip Distribution ($20k Order @ 50ms Latency)")
    ax1.set_xlabel("Slippage (USD Price Impact)")
    ax1.set_ylabel("Frequency of Occurrence")
    
    # Optional overlay: average fill probability line 
    avg_slip = results_df['execution_slip'].mean()
    plt.axvline(avg_slip, color='cyan', linestyle='dashed', linewidth=2, label=f'Avg Slip: ${avg_slip:.2f}')
    plt.legend()
    
    output_path = "artifacts/execution_slip_distribution.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Artifact Saved to: {output_path}")

if __name__ == "__main__":
    main()
