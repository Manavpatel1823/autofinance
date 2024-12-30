from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage

from auto_finance.agents.base import BaseAgent
from auto_finance.agents.analysis_agent import StockAnalysisAgent
from auto_finance.agents.types import AgentResponse, Portfolio, PortfolioRecommendation, Position
from auto_finance.tools.market_data import MarketDataTool

class PortfolioAgent(BaseAgent):
    """Agent for managing and optimizing a stock portfolio"""
    
    def __init__(
        self,
        *args,
        max_position_size: float = 0.20,  # Maximum 20% in single position
        min_position_size: float = 0.02,  # Minimum 2% in single position
        rebalance_threshold: float = 0.05,  # 5% deviation triggers rebalance
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.analysis_agent = StockAnalysisAgent(*args, **kwargs)
        self.market_tool = MarketDataTool()
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.rebalance_threshold = rebalance_threshold
        
    def run(
        self,
        portfolio: Portfolio,
        action: str = "analyze",
        **kwargs
    ) -> AgentResponse:
        """
        Run portfolio analysis and management tasks
        
        Args:
            portfolio: Current portfolio state
            action: Type of analysis to perform (analyze/rebalance/optimize)
            **kwargs: Additional parameters for specific actions
            
        Returns:
            AgentResponse with analysis and recommendations
        """
        try:
            # Update portfolio with current market data
            updated_portfolio = self._update_portfolio_data(portfolio)
            
            if action == "analyze":
                return self._analyze_portfolio(updated_portfolio)
            elif action == "rebalance":
                return self._rebalance_portfolio(updated_portfolio)
            elif action == "optimize":
                return self._optimize_portfolio(updated_portfolio, **kwargs)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Portfolio analysis failed: {str(e)}",
                error=str(e)
            )
    
    def _update_portfolio_data(self, portfolio: Portfolio) -> Portfolio:
        """Update portfolio with current market data"""
        total_value = portfolio.metrics.cash_balance
        
        for position in portfolio.positions:
            # Get current market data
            stock_data = self.market_tool.get_stock_data(position.symbol)
            
            # Update position metrics
            position.current_price = stock_data.current_price
            position.current_value = position.shares * position.current_price
            position.profit_loss = position.current_value - (position.shares * position.average_cost)
            position.profit_loss_percent = (
                (position.current_price - position.average_cost) / position.average_cost * 100
            )
            position.last_updated = datetime.now()
            
            total_value += position.current_value
        
        # Update portfolio weights
        for position in portfolio.positions:
            position.weight = position.current_value / total_value * 100
        
        # Update portfolio metrics
        portfolio.metrics.total_value = total_value
        portfolio.metrics.invested_value = total_value - portfolio.metrics.cash_balance
        portfolio.metrics.total_profit_loss = sum(p.profit_loss for p in portfolio.positions)
        portfolio.metrics.total_profit_loss_percent = (
            portfolio.metrics.total_profit_loss / portfolio.metrics.invested_value * 100
            if portfolio.metrics.invested_value > 0 else 0
        )
        
        return portfolio
    
    def _analyze_portfolio(self, portfolio: Portfolio) -> AgentResponse:
        """Perform comprehensive portfolio analysis"""
        # Prepare analysis data
        analysis_data = {
            "portfolio_summary": self._get_portfolio_summary(portfolio),
            "risk_analysis": self._analyze_risk(portfolio),
            "diversity_analysis": self._analyze_diversity(portfolio),
            "recommendations": self._generate_recommendations(portfolio)
        }
        
        # Prepare prompt for LLM analysis
        prompt = self._prepare_portfolio_prompt(portfolio, analysis_data)
        
        # Get LLM insights
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return AgentResponse(
            success=True,
            message="Portfolio analysis completed",
            data={
                "analysis": analysis_data,
                "llm_insights": response.content,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _rebalance_portfolio(self, portfolio: Portfolio) -> AgentResponse:
        """Generate portfolio rebalancing recommendations"""
        recommendations = []
        
        # Check for overweight positions
        for position in portfolio.positions:
            if position.weight > self.max_position_size * 100:
                target_value = portfolio.metrics.total_value * self.max_position_size
                shares_to_sell = int(
                    (position.current_value - target_value) / position.current_price
                )
                recommendations.append(
                    PortfolioRecommendation(
                        action="SELL",
                        symbol=position.symbol,
                        shares=shares_to_sell,
                        reason="Position exceeds maximum allocation",
                        priority=1,
                        expected_impact="Reduce portfolio risk through better diversification"
                    )
                )
        
        # Check for underweight positions
        if portfolio.target_allocations:
            for symbol, target_weight in portfolio.target_allocations.items():
                current_position = next(
                    (p for p in portfolio.positions if p.symbol == symbol),
                    None
                )
                if current_position:
                    if current_position.weight < target_weight - self.rebalance_threshold * 100:
                        target_value = portfolio.metrics.total_value * (target_weight / 100)
                        shares_to_buy = int(
                            (target_value - current_position.current_value) /
                            current_position.current_price
                        )
                        recommendations.append(
                            PortfolioRecommendation(
                                action="BUY",
                                symbol=symbol,
                                shares=shares_to_buy,
                                reason="Position below target allocation",
                                priority=2,
                                expected_impact="Better align with target allocation"
                            )
                        )
        
        return AgentResponse(
            success=True,
            message="Rebalancing analysis completed",
            data={
                "recommendations": [rec.dict() for rec in recommendations],
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _optimize_portfolio(
        self,
        portfolio: Portfolio,
        target_return: Optional[float] = None
    ) -> AgentResponse:
        """Optimize portfolio based on modern portfolio theory"""
        # Get historical data for all positions
        position_data = {}
        for position in portfolio.positions:
            stock_data = self.market_tool.get_stock_data(position.symbol, period="1y")
            position_data[position.symbol] = stock_data
        
        # Calculate optimal weights (simplified example)
        # In a real implementation, you would use more sophisticated optimization
        optimization_results = self._calculate_optimal_weights(
            position_data,
            portfolio.risk_tolerance,
            target_return
        )
        
        return AgentResponse(
            success=True,
            message="Portfolio optimization completed",
            data={
                "current_weights": {p.symbol: p.weight for p in portfolio.positions},
                "optimal_weights": optimization_results,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _get_portfolio_summary(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Generate portfolio summary statistics"""
        return {
            "total_positions": len(portfolio.positions),
            "largest_position": max(p.weight for p in portfolio.positions),
            "smallest_position": min(p.weight for p in portfolio.positions),
            "avg_position_size": sum(p.weight for p in portfolio.positions) / len(portfolio.positions),
            "cash_percentage": (
                portfolio.metrics.cash_balance / portfolio.metrics.total_value * 100
            )
        }
    
    def _analyze_risk(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Analyze portfolio risk metrics"""
        # This would typically include more sophisticated risk analysis
        return {
            "concentration_risk": self._calculate_concentration_risk(portfolio),
            "market_risk": self._calculate_market_risk(portfolio),
            "volatility": self._calculate_portfolio_volatility(portfolio)
        }
    
    def _analyze_diversity(self, portfolio: Portfolio) -> Dict[str, float]:
        """Analyze portfolio diversity across sectors and asset types"""
        # Get sector information for each position
        sector_weights = {}
        for position in portfolio.positions:
            stock_data = self.market_tool.get_stock_data(position.symbol)
            sector = getattr(stock_data, 'sector', 'Unknown')
            sector_weights[sector] = sector_weights.get(sector, 0) + position.weight
        
        # Calculate diversity score (simplified)
        num_sectors = len(sector_weights)
        max_sector_weight = max(sector_weights.values())
        
        diversity_score = (1 - (max_sector_weight / 100)) * (num_sectors / 11)  # 11 major sectors
        
        return {
            "diversity_score": diversity_score,
            "sector_weights": sector_weights
        }
    
    def _generate_recommendations(
        self,
        portfolio: Portfolio
    ) -> List[PortfolioRecommendation]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Check for rebalancing needs
        rebalance_recs = self._rebalance_portfolio(portfolio)
        if rebalance_recs.success and rebalance_recs.data:
            recommendations.extend(rebalance_recs.data["recommendations"])
        
        # Check for risk-based recommendations
        risk_analysis = self._analyze_risk(portfolio)
        if risk_analysis["concentration_risk"] > 0.7:  # High concentration risk
            recommendations.append(
                PortfolioRecommendation(
                    action="REBALANCE",
                    reason="High portfolio concentration risk",
                    priority=1,
                    expected_impact="Reduce portfolio risk through diversification"
                )
            )
        
        return recommendations
    
    def _prepare_portfolio_prompt(
        self,
        portfolio: Portfolio,
        analysis_data: Dict[str, Any]
    ) -> str:
        """Prepare prompt for LLM analysis"""
        return f"""
        Analyze the following portfolio data and provide strategic recommendations:
        
        Portfolio Summary:
        - Total Value: ${portfolio.metrics.total_value:,.2f}
        - Total Positions: {len(portfolio.positions)}
        - Cash Balance: ${portfolio.metrics.cash_balance:,.2f}
        - Total P/L: ${portfolio.metrics.total_profit_loss:,.2f} ({portfolio.metrics.total_profit_loss_percent:.1f}%)
        
        Risk Profile:
        - Risk Tolerance: {portfolio.risk_tolerance}
        - Investment Horizon: {portfolio.investment_horizon}
        - Diversity Score: {analysis_data['diversity_analysis']['diversity_score']:.2f}
        
        Current Positions:
        {self._format_positions(portfolio.positions)}
        
        Please provide:
        1. Overall portfolio health assessment
        2. Key risks and opportunities
        3. Specific recommendations for improvement
        4. Suggested position adjustments
        """
    
    def _format_positions(self, positions: List[Position]) -> str:
        """Format positions for the prompt"""
        position_str = ""
        for pos in positions:
            position_str += (
                f"- {pos.symbol}: {pos.shares} shares, "
                f"Value: ${pos.current_value:,.2f} ({pos.weight:.1f}%), "
                f"P/L: {pos.profit_loss_percent:.1f}%\n"
            )
        return position_str
    
    def _calculate_concentration_risk(self, portfolio: Portfolio) -> float:
        """Calculate portfolio concentration risk (0-1)"""
        weights = [p.weight / 100 for p in portfolio.positions]
        return sum(w * w for w in weights)  # Herfindahl-Hirschman Index
    
    def _calculate_market_risk(self, portfolio: Portfolio) -> float:
        """Calculate portfolio market risk (beta)"""
        # Simplified market risk calculation
        # In a real implementation, you would calculate proper portfolio beta
        return 1.0
    
    def _calculate_portfolio_volatility(self, portfolio: Portfolio) -> float:
        """Calculate portfolio volatility"""
        # Simplified volatility calculation
        # In a real implementation, you would use historical returns
        return 0.15  # Example annualized volatility
    
    def _calculate_optimal_weights(
        self,
        position_data: Dict[str, Any],
        risk_tolerance: str,
        target_return: Optional[float]
    ) -> Dict[str, float]:
        """Calculate optimal portfolio weights"""
        # Simplified optimization
        # In a real implementation, you would use proper portfolio optimization
        return {symbol: 1.0 / len(position_data) for symbol in position_data}