import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def trending_ohlcv_data():
    """Generates 50 periods of synthetic strongly trending OHLCV data."""
    dates = pd.date_range("2026-01-01", periods=50, freq="min")
    # Base price goes up exponentially. Add volatility to expand Bollinger Bands.
    base = np.exp(np.linspace(1, 6, 50))
    volatility = np.linspace(10, 100, 50) # Expand volatility
    data = {"high": base + volatility, "low": base - volatility, "close": base + (volatility / 2)}
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def ranging_ohlcv_data():
    """Generates 50 periods of synthetic completely flat ranging OHLCV data."""
    dates = pd.date_range("2026-01-01", periods=50, freq="min")
    # Base oscillates around 500
    base = 500 + np.sin(np.linspace(0, 50, 50)) * 5
    data = {"high": base + 10, "low": base - 10, "close": base + np.random.normal(0, 1, 50)}
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def historic_backtest_data():
    """Generates 10 periods of synthetic arbitrage opportunity data."""
    # Data isn't used inherently for calculation inside the backtest engine because
    # strategy logic consumes the row. We just need iterables.
    dates = pd.date_range("2026-01-01", periods=10, freq="s")
    df = pd.DataFrame({"dummy": range(10)}, index=dates)
    return df
