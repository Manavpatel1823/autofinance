import logging
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd
import yfinance as yf

from auto_finance.tools.market_data import MarketDataTool, StockData
from auto_finance.tools.news_data import NewsDataTool, NewsArticle
from auto_finance.tools.technical_indicators import TechnicalAnalysis
from auto_finance.agents.base import BaseAgent
from auto_finance.agents.types import AgentResponse, AnalysisRequest
from auto_finance.prompts.stock_analysis_prompt import StockAnalysisPrompts
from auto_finance.schemas.analysis_schema import StockAnalysisResponse

class StockAnalysisAgent(BaseAgent):
    """Agent for comprehensive stock analysis"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.market_tool = MarketDataTool()
        self.news_tool = NewsDataTool()
        
        # Add tools to the agent
        self.tools = [
            Tool(
                name="get_stock_data",
                func=self.market_tool.get_stock_data,
                description="Get stock market data including price and fundamentals"
            ),
            Tool(
                name="get_stock_news",
                func=self.news_tool.get_stock_news,
                description="Get recent news articles about a stock"
            )
        ]
    
    def _get_historical_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Get historical OHLCV data for technical analysis"""
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    
    def _gather_technical_data(self, symbol: str) -> Dict[str, Any]:
        """Gather and process technical indicators"""
        # Get historical data
        hist_data = self._get_historical_data(symbol)
        
        # Initialize technical analysis with historical data
        technical = TechnicalAnalysis(hist_data)
        return technical.run_analysis()
    
    def run(self, request: AnalysisRequest) -> AgentResponse:
        """
        Perform comprehensive stock analysis
        
        Args:
            request: AnalysisRequest object containing analysis parameters
            
        Returns:
            AgentResponse with detailed analysis and recommendations
        """
        try:
            # Gather data
            stock_data = self._gather_stock_data(request.symbol)
            news_data = self._gather_news_data(request.symbol) if request.include_news else []
            technical_data = self._gather_technical_data(request.symbol) if request.include_technicals else {}
            
            # Get LLM analysis
            analysis = self._analyze_stock(request, stock_data, news_data, technical_data)
            return AgentResponse(
                success=True,
                message="Analysis completed successfully",
                data=analysis.dict()
            )
            
        except Exception as e:
            logging.error(f"Analysis failed: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                message="Analysis failed",
                error=str(e)
            )
    
    def _gather_stock_data(self, symbol: str) -> StockData:
        """Gather comprehensive stock data"""
        return self.market_tool.get_stock_data(symbol)
    
    def _gather_news_data(self, symbol: str) -> List[NewsArticle]:
        """Gather and process news data"""
        news = self.news_tool.get_stock_news(symbol, max_articles=20)

        news_text = [article.title for article in news] 
        news_text = " ".join(news_text)
        
        sentiment = self.news_tool.analyze_sentiment(news_text)
        return {'articles': news_text, 'sentiment': sentiment}

    def _analyze_stock(
        self,
        request: AnalysisRequest,
        stock_data: StockData,
        news_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> StockAnalysisResponse:
        """Perform comprehensive stock analysis"""
        # Prepare prompt data
        prompt_data = self._prepare_prompt_data(
            request, stock_data, news_data, technical_data
        )
        
        # Get prompts
        system_prompt = StockAnalysisPrompts.SYSTEM_PROMPT
        analysis_prompt = StockAnalysisPrompts.get_analysis_prompt(prompt_data)
        
        # Get LLM analysis
        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        # Parse and validate response
        try:
            analysis = StockAnalysisResponse.parse_raw_response(response.content)
            return analysis
        except ValueError as e:
            logging.error(f"Failed to parse LLM response: {str(e)}")
            raise
    
    def _prepare_prompt_data(
        self,
        request: AnalysisRequest,
        stock_data: StockData,
        news_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for prompt template"""
        # Format market cap
        market_cap = self._format_market_cap(stock_data.market_cap)
        
        # Format dividend yield
        dividend_yield = (
            f"{stock_data.dividend_yield:.2f}%" 
            if stock_data.dividend_yield is not None 
            else "N/A"
        )
        
        # Get MACD data
        macd_data = technical_data.get('macd', {})
        bb_data = technical_data.get('bollinger_bands', {})
        
        return {
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'risk_tolerance': request.risk_tolerance,
            'current_price': f"{stock_data.current_price:.2f}",
            'price_change': f"{stock_data.price_change_6m:.1f}%",
            'rsi': f"{stock_data.rsi:.1f}",
            'ma_50': f"{stock_data.ma_50:.2f}",
            'ma_200': f"{stock_data.ma_200:.2f}",
            'macd': macd_data.get('macd', 'N/A'),
            'signal': macd_data.get('signal', 'N/A'),
            'histogram': macd_data.get('histogram', 'N/A'),
            'bb_upper': bb_data.get('upper', 'N/A'),
            'bb_middle': bb_data.get('middle', 'N/A'),
            'bb_lower': bb_data.get('lower', 'N/A'),
            'pe_ratio': stock_data.pe_ratio,
            'market_cap': market_cap,
            'dividend_yield': dividend_yield,
            'eps': stock_data.eps,
            'news_sentiment': news_data.get('sentiment', (0, 'neutral'))[1],
            'news_headlines': [
                article.title for article in news_data.get('articles', [])[:5]
            ]
        }
    
    def _format_market_cap(self, market_cap: Optional[float]) -> str:
        """Format market cap in billions/millions"""
        if not market_cap:
            return "N/A"
        
        if market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        else:
            return f"${market_cap/1e6:.1f}M"
    
    def _calculate_technical_score(
        self,
        stock_data: StockData,
        technical_data: Dict[str, Any]
    ) -> float:
        """Calculate technical analysis score (0-10)"""
        score = 5.0  # Start with neutral score
        
        # Trend analysis
        if stock_data.ma_50 > stock_data.ma_200:
            score += 1  # Positive trend
        else:
            score -= 1  # Negative trend
        
        # RSI analysis
        if 30 <= stock_data.rsi <= 70:
            score += 1  # Healthy RSI
        elif stock_data.rsi < 30:
            score += 0.5  # Oversold
        else:
            score -= 1  # Overbought
        
        # MACD analysis
        if technical_data.get('macd', {}).get('histogram', 0) > 0:
            score += 1
        
        # Bollinger Bands analysis
        bb = technical_data.get('bollinger_bands', {})
        if stock_data.current_price < bb.get('lower', float('inf')):
            score += 1  # Below lower band
        elif stock_data.current_price > bb.get('upper', 0):
            score -= 1  # Above upper band
        
        return max(0, min(10, score))  # Ensure score is between 0-10
    
    def _calculate_fundamental_score(self, stock_data: StockData) -> float:
        """Calculate fundamental analysis score (0-10)"""
        score = 5.0  # Start with neutral score
        
        # P/E Ratio analysis
        if stock_data.pe_ratio:
            if 0 < stock_data.pe_ratio < 15:
                score += 2  # Attractive P/E
            elif 15 <= stock_data.pe_ratio < 25:
                score += 1  # Reasonable P/E
            elif stock_data.pe_ratio >= 35:
                score -= 1  # High P/E
        
        # Dividend analysis
        if stock_data.dividend_yield:
            if stock_data.dividend_yield > 4:
                score += 1.5  # High dividend
            elif stock_data.dividend_yield > 2:
                score += 1  # Good dividend
        
        # Market cap analysis (prefer established companies)
        if stock_data.market_cap:
            if stock_data.market_cap > 200e9:  # Large cap
                score += 1
            elif stock_data.market_cap < 2e9:  # Small cap
                score -= 0.5
        
        return max(0, min(10, score))  # Ensure score is between 0-10
    
    def _calculate_sentiment_score(self, news_data: Dict[str, Any]) -> float:
        """Calculate news sentiment score (0-10)"""
        base_score = 5.0
        sentiment = news_data.get('sentiment', 0)
        
        # Convert sentiment (-1 to 1) to score (0-10)
        score = base_score + (sentiment * 5)
        
        return max(0, min(10, score))  # Ensure score is between 0-10
    
    def _format_market_cap(self, market_cap: Optional[float]) -> str:
        """Format market cap in billions/millions"""
        if not market_cap:
            return "N/A"
        
        if market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        else:
            return f"${market_cap/1e6:.1f}M"
    
    def _format_news_headlines(self, articles: List[NewsArticle]) -> str:
        """Format news headlines for prompt"""
        if not articles:
            return "No recent news available"
        
        headlines = []
        for article in articles[:5]:  # Latest 5 articles
            # Safely handle date formatting
            try:
                date_str = article.date
                title = article.title if article.title else "No title available"
                headlines.append(f"- {title} ({date_str})")
            except AttributeError:
                continue
        return "\n".join(headlines) if headlines else "No recent news available"
    
    def _parse_llm_analysis(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured data
        Note: This implementation would need to be customized based on your LLM's output format
        """
        # This is a simplified parser - you would need to implement proper parsing
        # based on your LLM's output structure
        return {
            'recommendation': 'HOLD',
            'confidence_level': 0.8,
            'summary': llm_response,
            'technical_analysis': {},
            'fundamental_analysis': {},
            'news_analysis': {},
            'risk_factors': [],
            'opportunities': [],
            'price_targets': {
                'short_term': 0,
                'medium_term': 0,
                'long_term': 0
            }
        }