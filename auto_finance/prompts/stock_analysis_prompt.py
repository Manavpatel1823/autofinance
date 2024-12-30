from string import Template
from typing import Dict, Any

class StockAnalysisPrompts:
    """Collection of prompts for stock analysis"""
    
    SYSTEM_PROMPT = """You are a financial analyst assistant specializing in stock analysis. 
    Your analysis should be data-driven, comprehensive, and formatted according to the specified JSON schema.
    Always provide analysis with supporting evidence and maintain a balanced perspective."""

    ANALYSIS_TEMPLATE = Template("""
    Analyze the following data for ${symbol} and provide a structured analysis report.
    Consider the ${timeframe} timeframe and ${risk_tolerance} risk tolerance level.

    Technical Indicators:
    - Current Price: $${current_price}
    - 6-Month Price Change: ${price_change}
    - RSI: ${rsi}
    - 50-day MA: $${ma_50}
    - 200-day MA: $${ma_200}

    MACD Analysis:
    - MACD: ${macd}
    - Signal: ${signal}
    - Histogram: ${histogram}

    Bollinger Bands:
    - Upper: ${bb_upper}
    - Middle: ${bb_middle}
    - Lower: ${bb_lower}

    Fundamental Data:
    - P/E Ratio: ${pe_ratio}
    - Market Cap: ${market_cap}
    - Dividend Yield: ${dividend_yield}
    - EPS: ${eps}

    Recent News Sentiment: ${news_sentiment}

    Recent News Headlines:
    ${news_headlines}

    Provide a comprehensive analysis in the following JSON format:
    {
        "recommendation": "BUY/HOLD/SELL",
        "confidence_level": 0.0-1.0,
        "summary": "Overall analysis summary",
        "technical_analysis": {
            "trend": "Overall trend analysis",
            "support_levels": [price levels],
            "resistance_levels": [price levels],
            "momentum": "Momentum analysis",
            "volume_analysis": "Volume trend analysis"
        },
        "fundamental_analysis": {
            "valuation": "Valuation analysis",
            "growth_potential": "Growth analysis",
            "financial_health": "Financial health assessment",
            "competitive_position": "Market position analysis",
            "industry_outlook": "Industry/sector analysis"
        },
        "news_analysis": {
            "overall_sentiment": "Overall news sentiment"(positive|negative|neutral|mixed),
            "key_developments": ["Important recent developments"],
            "market_perception": "Market perception analysis"
        },
        "risk_factors": ["Key risk factors"],
        "opportunities": ["Key opportunities"],
        "price_targets": {
            "short_term": price,
            "medium_term": price,
            "long_term": price
        }
    }

    Ensure your response is valid JSON and includes all required fields.""")

    @classmethod
    def get_analysis_prompt(cls, data: Dict[str, Any]) -> str:
        """
        Generate analysis prompt from template and data
        
        Args:
            data: Dictionary containing template variables
            
        Returns:
            Formatted prompt string
        """
        # Format special fields
        data['news_headlines'] = '\n'.join([
            f"- {headline}" for headline in data.get('news_headlines', [])
        ])
        
        # Set defaults for optional fields
        defaults = {
            'macd': 'N/A',
            'signal': 'N/A',
            'histogram': 'N/A',
            'bb_upper': 'N/A',
            'bb_middle': 'N/A',
            'bb_lower': 'N/A',
            'news_sentiment': 'N/A',
            'pe_ratio': 'N/A',
            'dividend_yield': 'N/A',
            'eps': 'N/A'
        }
        
        # Merge defaults with provided data
        prompt_data = {**defaults, **data}
        
        return cls.ANALYSIS_TEMPLATE.safe_substitute(prompt_data)