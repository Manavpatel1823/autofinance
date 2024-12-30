import csv
import os
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
        print("Analyzing ticker: ", ticker)
        request = AnalysisRequest(
            symbol=ticker,
            include_technicals=True,
            include_fundamentals=True,
            include_news=True,
            timeframe="medium",
            risk_tolerance="moderate"
        )
        
        result = agent.run(request)
        results.append(result)
        
    return results


def analyze_portfolio(input_csv: str, output_csv: str, container: Container):
    """
    Analyze stocks from a portfolio CSV file and save results to a new CSV.
    
    Args:
        input_csv: Path to the input CSV file
        output_csv: Path to the output CSV file
        container: DI container
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file '{input_csv}' does not exist.")
    
    portfolio = []
    with open(input_csv, mode='r') as infile:
        reader = csv.DictReader(infile)
        portfolio = list(reader)
    
    tickers = [row['Symbol'] for row in portfolio]
    results = analyze_stocks(tickers, container)
    
    # Add analysis results to portfolio
    for row, result in zip(portfolio, results):
        if result.success:
            analysis = result.data
            row['Recommendation'] = analysis['recommendation']
            row['Confidence Level'] = analysis['confidence_level']
            row['Short Term Price Target'] = analysis['price_targets']['short_term']
            row['Medium Term Price Target'] = analysis['price_targets']['medium_term']
            row['Long Term Price Target'] = analysis['price_targets']['long_term']
        else:
            row['Recommendation'] = "Error"
            row['Confidence Level'] = "N/A"
            row['Short Term Price Target'] = "N/A"
            row['Medium Term Price Target'] = "N/A"
            row['Long Term Price Target'] = "N/A"
        print(row)
    
    # Write updated portfolio to output CSV
    fieldnames = list(portfolio[0].keys())
    with open(output_csv, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(portfolio)


def handle(args, cwd):
    """Handle the analyze_stock command"""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize container with config
        container = Container()
        container.config.from_dict(config)
        
        # Perform portfolio analysis
        analyze_portfolio(args.input_csv, args.output_csv, container)
        print(f"Portfolio analysis completed. Results saved to {args.output_csv}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def setup(subparsers):
    """Setup the command line parser"""
    analyze_stock_parser = subparsers.add_parser(
        "analyze_stock",
        help="Analyze a portfolio of stocks from a CSV file"
    )

    analyze_stock_parser.add_argument(
        "--input-csv",
        required=True,
        help="Path to the input portfolio CSV file"
    )

    analyze_stock_parser.add_argument(
        "--output-csv",
        required=True,
        help="Path to the output CSV file to save analysis results"
    )
    
    return analyze_stock_parser
