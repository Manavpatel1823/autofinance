from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pydantic import BaseModel

class TechnicalIndicators:
    """Collection of technical analysis indicators"""
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=fast_period, adjust=False).mean()
        exp2 = prices.ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        window: int = 20,
        num_std: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        middle_band = prices.rolling(window=window).mean()
        std_dev = prices.rolling(window=window).std()
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_stochastic_oscillator(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_line = k_line.rolling(window=d_period).mean()
        return k_line, d_line
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume (OBV)"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        return obv
    
    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average True Range (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_fibonacci_retracement(
        high_price: float,
        low_price: float
    ) -> Dict[str, float]:
        """Calculate Fibonacci Retracement Levels"""
        diff = high_price - low_price
        levels = {
            '0.0': low_price,
            '0.236': low_price + (diff * 0.236),
            '0.382': low_price + (diff * 0.382),
            '0.5': low_price + (diff * 0.5),
            '0.618': low_price + (diff * 0.618),
            '0.786': low_price + (diff * 0.786),
            '1.0': high_price
        }
        return levels

class TechnicalAnalysis:
    """Comprehensive technical analysis tool"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with price data
        
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data
        self.indicators = TechnicalIndicators()
        
    def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive technical analysis"""
        results = {}
        
        # Calculate all indicators
        macd, signal, hist = self.indicators.calculate_macd(self.data['Close'])
        upper_bb, middle_bb, lower_bb = self.indicators.calculate_bollinger_bands(
            self.data['Close']
        )
        k_line, d_line = self.indicators.calculate_stochastic_oscillator(
            self.data['High'],
            self.data['Low'],
            self.data['Close']
        )
        obv = self.indicators.calculate_obv(self.data['Close'], self.data['Volume'])
        atr = self.indicators.calculate_atr(
            self.data['High'],
            self.data['Low'],
            self.data['Close']
        )
        
        # Store latest values
        results['macd'] = {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': hist.iloc[-1]
        }
        
        results['bollinger_bands'] = {
            'upper': upper_bb.iloc[-1],
            'middle': middle_bb.iloc[-1],
            'lower': lower_bb.iloc[-1]
        }
        
        results['stochastic'] = {
            'k_line': k_line.iloc[-1],
            'd_line': d_line.iloc[-1]
        }
        
        results['other_indicators'] = {
            'obv': obv.iloc[-1],
            'atr': atr.iloc[-1]
        }
        
        # Calculate Fibonacci levels using recent high/low
        recent_high = self.data['High'].tail(20).max()
        recent_low = self.data['Low'].tail(20).min()
        results['fibonacci'] = self.indicators.calculate_fibonacci_retracement(
            recent_high,
            recent_low
        )
        
        return results