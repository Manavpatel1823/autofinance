from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from urllib.parse import urlencode

class NewsArticle(BaseModel):
    title: str
    date: str
    time: str
    source: str
    url: Optional[str] = None
    current_price: Optional[float] = None

class NewsDataTool:
    """Tool for fetching and processing financial news data"""
    
    API_KEY = "fIpWmHOoNrHz_syKnRyDVYkzvKtQmup9"

    @staticmethod
    def get_current_price(symbol: str) -> float:
        """
        Fetch the current price of the stock using Polygon.io API.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Current stock price as a float
        """
        try:
            base_url = "https://api.polygon.io/v2/last/trade"
            url = f"{base_url}/{symbol}?apiKey={NewsDataTool.API_KEY}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for bad HTTP responses
            data = response.json()
            
            # Extract the price from the response
            if "results" in data and "p" in data["results"]:
                return data["results"]["p"]  # 'p' stands for the price
            else:
                print("Price data not found.")
                return -1.0
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return -1.0

    @staticmethod
    def get_stock_news(
        symbol: str,
        max_articles: int = 10,
        days_back: int = 7
    ) -> List[NewsArticle]:
        """
        Fetch recent news articles about the stock
        
        Args:
            symbol: Stock ticker symbol
            max_articles: Maximum number of articles to return
            days_back: How many days back to look for news
            
        Returns:
            List of NewsArticle objects
        """

        # Calculate the start date based on days_back
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days_back)

        # Prepare API endpoint
        base_url = "https://api.polygon.io/v2/reference/news"
        params = {
            "ticker": symbol,
            "limit": max_articles,
            "published_utc.gte": start_date.isoformat(),
            "apiKey": NewsDataTool.API_KEY,
        }
        url = f"{base_url}?{urlencode(params)}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            data = response.json()
            
            if "results" not in data or not data["results"]:
                print(f"No news articles found for {symbol}.")
                return []
            
            current_price = NewsDataTool.get_current_price(symbol)
            if current_price == -1.0:
                print("Unable to fetch the current price.")

            news_list = []
            for article in data["results"]:
                news_article = NewsArticle(
                    title=article.get("title", "No Title"),
                    date=article.get("published_utc", "Unknown Date").split("T")[0],
                    time=article.get("published_utc", "Unknown Time").split("T")[-1],
                    source=article.get("publisher", {}).get("name", "Unknown Source"),
                    current_price=current_price,
                    url=article.get("article_url", None),
                )
                news_list.append(news_article)

                if len(news_list) >= max_articles:
                    break

            return news_list

        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    @staticmethod
    def analyze_sentiment(articles: List[NewsArticle]) -> float:
        """
        Perform basic sentiment analysis on news articles
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            Sentiment score between -1 and 1
        """
        positive_keywords = {
            'surge', 'jump', 'rise', 'gain', 'growth', 'positive', 'bullish',
            'outperform', 'beat', 'exceeded'
        }
        negative_keywords = {
            'fall', 'drop', 'decline', 'negative', 'risk', 'concern', 'bearish',
            'underperform', 'miss', 'below'
        }
        
        total_score = 0
        for article in articles:
            title_words = article.title.lower().split()
            pos_count = sum(1 for word in positive_keywords if word in title_words)
            neg_count = sum(1 for word in negative_keywords if word in title_words)
            
            article_score = (pos_count - neg_count) / max(pos_count + neg_count, 1)
            total_score += article_score
            
        return total_score / len(articles) if articles else 0