

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field



class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
class Position(BaseModel):
    """Model representing a single portfolio position"""
    symbol: str
    shares: int
    average_cost: float
    current_price: float = Field(default=0.0)
    current_value: float = Field(default=0.0)
    profit_loss: float = Field(default=0.0)
    profit_loss_percent: float = Field(default=0.0)
    weight: float = Field(default=0.0)  # Portfolio weight as percentage
    last_updated: datetime = Field(default_factory=datetime.now)

class PortfolioMetrics(BaseModel):
    """Model for portfolio performance metrics"""
    total_value: float
    cash_balance: float
    invested_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    sharpe_ratio: Optional[float] = None
    beta: Optional[float] = None
    alpha: Optional[float] = None
    diversity_score: float  # 0-1 score based on sector/asset diversification

class PortfolioRecommendation(BaseModel):
    """Model for portfolio recommendations"""
    action: str  # "BUY", "SELL", "REBALANCE"
    symbol: Optional[str] = None
    shares: Optional[int] = None
    reason: str
    priority: int  # 1-5, where 1 is highest priority
    expected_impact: str

class Portfolio(BaseModel):
    """Model representing the complete portfolio"""
    positions: List[Position]
    metrics: PortfolioMetrics
    risk_tolerance: str = "moderate"
    investment_horizon: str = "medium"  # short/medium/long
    target_allocations: Optional[Dict[str, float]] = None  # Target allocation by sector


class AnalysisRequest(BaseModel):
    """Model for stock analysis request parameters"""
    symbol: str
    include_technicals: bool = True
    include_fundamentals: bool = True
    include_news: bool = True
    timeframe: str = "medium"  # short/medium/long
    risk_tolerance: str = "moderate"  # conservative/moderate/aggressive

class AnalysisMetrics(BaseModel):
    """Model for analysis metrics"""
    technical_score: float = Field(ge=0, le=10)
    fundamental_score: float = Field(ge=0, le=10)
    sentiment_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)
    confidence_level: float = Field(ge=0, le=1)

class StockAnalysis(BaseModel):
    """Model for complete stock analysis"""
    symbol: str
    timestamp: datetime
    metrics: AnalysisMetrics
    recommendation: str  # BUY/HOLD/SELL
    summary: str
    technical_analysis: Dict[str, Any]
    fundamental_analysis: Dict[str, Any]
    news_analysis: Dict[str, Any]
    risk_factors: List[str]
    opportunities: List[str]
    price_targets: Dict[str, float]  # short_term, medium_term, long_term