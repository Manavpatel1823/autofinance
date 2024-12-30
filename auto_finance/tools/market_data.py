from typing import Dict, Optional
import yfinance as yf
import pandas as pd
from pydantic import BaseModel

class StockData(BaseModel):
    symbol: str
    current_price: float
    price_change_6m: float
    avg_volume: float
    volatility: float
    ma_50: float
    ma_200: float
    rsi: float
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None

class MarketDataTool:
    """Tool for fetching and processing market data"""
    
    @staticmethod
    def get_stock_data(symbol: str, period: str = "6mo") -> StockData:
        """
        Fetch stock data using yfinance API
        
        Args:
            symbol: Stock ticker symbol
            period: Time period for historical data
            
        Returns:
            StockData object containing processed market data
        """
        stock = yf.Ticker(symbol)
        # Using fast_info property instead of basic_info method
        hist = stock.history(period=period)
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate key metrics
        metrics = {
            'symbol': symbol,
            'current_price': current_price,
            'price_change_6m': (
                (current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
            ) * 100,
            'avg_volume': hist['Volume'].mean(),
            'volatility': hist['Close'].pct_change().std() * 100,
            'ma_50': hist['Close'].rolling(window=50).mean().iloc[-1],
            'ma_200': hist['Close'].rolling(window=200).mean().iloc[-1],
            'rsi': MarketDataTool._calculate_rsi(hist['Close']).iloc[-1]
        }
        
        # Get additional financial data
        try:
            info = stock.info
            metrics.update({
                'pe_ratio': info.get('forwardPE'),
                'market_cap': info.get('marketCap'),
                'dividend_yield': info.get('dividendYield'),
                'eps': info.get('trailingEps')
            })
        except Exception:
            pass
        
        return StockData(**metrics)
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))