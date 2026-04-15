from strategies.regime_detection import RegimeDetectionEngine

def test_regime_detection_trending(trending_ohlcv_data):
    engine = RegimeDetectionEngine(adx_threshold=25, period=14, bb_std=2.0)
    # With the new dual-confirmation logic, expanding BBW handles the slow ADX stabilization
    regime = engine.detect_regime(trending_ohlcv_data)
    # A directional walk with expanding volatility should hit TRENDING
    assert regime == "TRENDING"

def test_regime_detection_ranging(ranging_ohlcv_data):
    engine = RegimeDetectionEngine(adx_threshold=25, period=14)
    regime = engine.detect_regime(ranging_ohlcv_data)
    # Perfect sinusoidal range-bound dataset without expansion should be < 25 ADX
    assert regime == "RANGING"

def test_regime_detection_unknown():
    engine = RegimeDetectionEngine(adx_threshold=25, period=14)
    # Give too little data (e.g. 5 periods when 28 is required for period=14 ADX calculation)
    import pandas as pd
    short_data = pd.DataFrame({"high": [1,2,3,4,5], "low": [1,2,3,4,5], "close": [1,2,3,4,5]})
    regime = engine.detect_regime(short_data)
    assert regime == "UNKNOWN"
