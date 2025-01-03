# auto_finance/actions/analyze_stock.py

from typing import List
from auto_finance.config.di import Container
from auto_finance.config.settings import load_config
from auto_finance.agents.types import AnalysisRequest, AgentResponse

def analyze_stocks(tickers: List[str], container: Container) -> List[AgentResponse]:
    """
    Analyze multiple stocks and return recommendations
    
    Args:
        tickers: List of stock ticker symbols
        container: DI container
        
    Returns:
        List of analysis results
    """
    agent = container.stock_analysis_agent()
    results = []
    
    for ticker in tickers:
        print("analysing ticker: ", ticker)
        request = AnalysisRequest(
            symbol=ticker,
            include_technicals=True,
            include_fundamentals=True,
            include_news=True,
            timeframe="medium",
            risk_tolerance="moderate"
        )
        
        result = agent.run(request)
        print("*****")
        print("result:->", result)
        print("****")

        results.append(result)
        
    return results

def handle(args, cwd):
    """Handle the analyze_stock command"""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize container with config
        container = Container()
        container.config.from_dict(config)
        
        # Parse tickers from comma-separated list
        tickers = [t.strip() for t in args.stock_ticker.split(',')]
        
        # Run analysis
        results = analyze_stocks(tickers, container)
        
        # Print results
        for result in results:
            if result.success:
                analysis = result.data

                print(f"\nAnalysis Results:")
                print("=" * 50)
                print(f"Recommendation: {analysis['recommendation']}")
                print(f"Confidence Level: {analysis['confidence_level']:.2f}")
                
                print("\nSummary:")
                print(analysis['summary'])
                
                print("\nTechnical Analysis:")
                print(f"Trend: {analysis['technical_analysis']['trend']}")
                print(f"Momentum: {analysis['technical_analysis']['momentum']}")
                print(f"Volume Analysis: {analysis['technical_analysis']['volume_analysis']}")
                if analysis['technical_analysis']['support_levels']:
                    print(f"Support Levels: {', '.join(map(str, analysis['technical_analysis']['support_levels']))}")
                if analysis['technical_analysis']['resistance_levels']:
                    print(f"Resistance Levels: {', '.join(map(str, analysis['technical_analysis']['resistance_levels']))}")
                
                print("\nFundamental Analysis:")
                print(f"Valuation: {analysis['fundamental_analysis']['valuation']}")
                print(f"Growth Potential: {analysis['fundamental_analysis']['growth_potential']}")
                print(f"Financial Health: {analysis['fundamental_analysis']['financial_health']}")
                print(f"Competitive Position: {analysis['fundamental_analysis']['competitive_position']}")
                print(f"Industry Outlook: {analysis['fundamental_analysis']['industry_outlook']}")
                
                print("\nNews Analysis:")
                print(f"Overall Sentiment: {analysis['news_analysis']['overall_sentiment']}")
                print(f"Market Perception: {analysis['news_analysis']['market_perception']}")
                if analysis['news_analysis']['key_developments']:
                    print("\nKey Developments:")
                    for dev in analysis['news_analysis']['key_developments']:
                        print(f"- {dev}")
                
                print("\nRisk Factors:")
                for risk in analysis['risk_factors']:
                    print(f"- {risk}")
                
                print("\nOpportunities:")
                for opp in analysis['opportunities']:
                    print(f"- {opp}")
                
                print("\nPrice Targets:")
                targets = analysis['price_targets']
                print(f"Short Term: ${targets['short_term']:.2f}")
                print(f"Medium Term: ${targets['medium_term']:.2f}")
                print(f"Long Term: ${targets['long_term']:.2f}")
                
                print("=" * 50)
            else:
                print(f"\nError analyzing stock: {result.error}")
                print("=" * 50)
                        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nPlease make sure:")
        print("1. You have created a .env file with your GOOGLE_API_KEY")
        print("2. The API key is valid and has access to the Gemini API")
        print("3. The environment variables are properly loaded")

def setup(subparsers):
    """Setup the command line parser"""
    analyze_stock_parser = subparsers.add_parser(
        "analyze_stock",
        help="Analyse one or more stocks"
    )

    analyze_stock_parser.add_argument(
        "--stock-ticker",
        required=True,
        help="Comma-separated list of stock tickers to analyze"
    )
    
    return analyze_stock_parser