from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

class NewsArticle(BaseModel):
    title: str
    date: str
    time: str
    source: str
    url: Optional[str] = None

class NewsDataTool:
    """Tool for fetching and processing financial news data"""
    
    @staticmethod
    def get_stock_news(
        symbol: str,
        max_articles: int = 5,
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
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            print("response", response)
            soup = BeautifulSoup(response.text, 'html.parser')
            attrs = soup.attrs()
            print("attrs: ")
            print(attrs)
            news_table = soup.find(id='news-table')
            print("news_table: ", news_table)
            
            news_list = []
            for row in news_table.findAll('tr'):
                title = row.a.text
                date_data = row.td.text.split(' ')
                
                if len(date_data) == 1:
                    time = date_data[0]
                    date = datetime.today().strftime('%Y-%m-%d')
                else:
                    date = date_data[0]
                    time = date_data[1]
                
                article = NewsArticle(
                    title=title,
                    date=date,
                    time=time,
                    source=row.span.text if row.span else "Unknown",
                    url=row.a['href'] if row.a else None
                )
                
                news_list.append(article)
                
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