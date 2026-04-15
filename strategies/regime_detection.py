import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("RegimeDetection")

class RegimeDetectionEngine:
    def __init__(self, adx_threshold=25, period=14):
        self.adx_threshold = adx_threshold
        self.period = period
        
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(self.period).mean()

    def calculate_adx(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average Directional Index (ADX) to determine trend strength."""
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        
        plus_dm[plus_dm < 0] = 0
        plus_dm[plus_dm < minus_dm] = 0
        
        minus_dm[minus_dm < 0] = 0
        minus_dm[minus_dm < plus_dm] = 0
        
        atr = self.calculate_atr(df)
        
        plus_di = 100 * (plus_dm.ewm(alpha=1/self.period).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/self.period).mean() / atr)
        
        dx = (np.abs(plus_di - minus_di) / np.abs(plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/self.period).mean()
        
        return adx

    def detect_regime(self,  ohlcv_df: pd.DataFrame) -> str:
        """
        Takes a dataframe with 'high', 'low', 'close' columns.
        Returns 'TRENDING' if ADX > threshold, else 'RANGING'.
        """
        if len(ohlcv_df) < self.period * 2:
            return "UNKNOWN" # Not enough data
            
        adx_series = self.calculate_adx(ohlcv_df)
        current_adx = adx_series.iloc[-1]
        
        if pd.isna(current_adx):
            return "UNKNOWN"
            
        if current_adx >= self.adx_threshold:
            logger.debug(f"Regime Detected: TRENDING (ADX: {current_adx:.2f})")
            return "TRENDING"
        else:
            logger.debug(f"Regime Detected: RANGING (ADX: {current_adx:.2f})")
            return "RANGING"
