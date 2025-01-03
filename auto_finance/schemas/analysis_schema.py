from typing import List, Optional
from pydantic import BaseModel, Field
import json

class TechnicalAnalysis(BaseModel):
    trend: str = Field(
        ...,
        description="Overall trend analysis",
        pattern="^(bullish|bearish|neutral|sideways)$"
    )
    support_levels: List[float] = Field(
        default=[],
        description="Key support price levels"
    )
    resistance_levels: List[float] = Field(
        default=[],
        description="Key resistance price levels"
    )
    momentum: str = Field(
        ...,
        description="Momentum analysis",
        min_length=1
    )
    volume_analysis: str = Field(
        ...,
        description="Volume trend analysis",
        min_length=1
    )

class FundamentalAnalysis(BaseModel):
    valuation: str = Field(..., min_length=1)
    growth_potential: str = Field(..., min_length=1)
    financial_health: str = Field(..., min_length=1)
    competitive_position: str = Field(..., min_length=1)
    industry_outlook: str = Field(..., min_length=1)

class NewsAnalysis(BaseModel):
    overall_sentiment: str = Field(
        ...,
        pattern="^(positive|negative|neutral|mixed|Neutral|Positive|Negative|Mixed)$"
    )
    key_developments: List[str] = Field(
        default=[],
        min_length=0
    )
    market_perception: str = Field(..., min_length=1)

class PriceTargets(BaseModel):
    short_term: float = Field(..., gt=0)
    medium_term: float = Field(..., gt=0)
    long_term: float = Field(..., gt=0)
    
    # @validator('medium_term')
    # def medium_term_validation(cls, v, values):
    #     if 'short_term' in values and v < values['short_term']:
    #         raise ValueError('Medium-term target should be >= short-term target')
    #     return v
    
    # @validator('long_term')
    # def long_term_validation(cls, v, values):
    #     if 'medium_term' in values and v < values['medium_term']:
    #         raise ValueError('Long-term target should be >= medium-term target')
    #     return v

class StockAnalysisResponse(BaseModel):
    """Schema for stock analysis response"""
    recommendation: str = Field(
        ...,
        pattern="^(BUY|HOLD|SELL)$"
    )
    confidence_level: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )
    summary: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )
    technical_analysis: TechnicalAnalysis
    fundamental_analysis: FundamentalAnalysis
    news_analysis: NewsAnalysis
    risk_factors: List[str] = Field(
        default=[],
        min_length=1
    )
    opportunities: List[str] = Field(
        default=[],
        min_length=1
    )
    price_targets: PriceTargets

    @classmethod
    def parse_raw_response(cls, response_text: str) -> 'StockAnalysisResponse':
        """
        Parse and validate raw LLM response
        
        Args:
            response_text: Raw JSON response from LLM
            
        Returns:
            Validated StockAnalysisResponse object
        """
        try:
            # Extract JSON from response text
            json_str = cls._extract_json(response_text)
            
            # Parse JSON to dict first to handle the trend field
            data = json.loads(json_str)
            
            # Clean up the trend field - extract just the trend value
            if 'technical_analysis' in data and 'trend' in data['technical_analysis']:
                trend_text = data['technical_analysis']['trend'].lower()
                if 'bullish' in trend_text:
                    data['technical_analysis']['trend'] = 'bullish'
                elif 'bearish' in trend_text:
                    data['technical_analysis']['trend'] = 'bearish'
                elif 'sideways' in trend_text:
                    data['technical_analysis']['trend'] = 'sideways'
                else:
                    data['technical_analysis']['trend'] = 'neutral'
            
            # Convert back to JSON
            cleaned_json = json.dumps(data)
            
            # Parse and validate
            return cls.model_validate_json(cleaned_json)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from text that might contain other content"""
        try:
            # Try to find JSON block
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = text[start_idx:end_idx]
            # Validate JSON is parseable
            json.loads(json_str)
            return json_str
        except Exception as e:
            raise ValueError(f"Failed to extract valid JSON: {str(e)}")