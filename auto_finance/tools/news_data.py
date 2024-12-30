from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import logging
from transformers import pipeline
import numpy as np

class NewsArticle(BaseModel):
    title: str
    date: str
    time: str
    source: str
    url: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None

class NewsDataTool:
    """Tool for fetching and processing financial news data"""
    
    def __init__(self):
        """Initialize the NewsDataTool with sentiment analyzer"""
        # Load the sentiment analysis pipeline
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",  # Financial domain-specific BERT
                truncation=True
            )
        except Exception as e:
            logging.error(f"Error loading sentiment model: {str(e)}")
            self.sentiment_analyzer = None
    
    @staticmethod
    def inspect_page_content(soup: BeautifulSoup) -> Dict:
        """
        Inspect the available content on the page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary containing information about available elements
        """
        page_info = {
            'tables': [],
            'divs_with_ids': [],
            'forms': [],
            'major_sections': []
        }
        
        # Find all tables and their IDs/classes
        for table in soup.find_all('table'):
            table_info = {
                'id': table.get('id', 'No ID'),
                'class': table.get('class', 'No Class'),
                'rows': len(table.find_all('tr'))
            }
            page_info['tables'].append(table_info)
            
        # Find divs with IDs
        for div in soup.find_all('div', id=True):
            page_info['divs_with_ids'].append(div['id'])
            
        # Find forms
        for form in soup.find_all('form'):
            form_info = {
                'id': form.get('id', 'No ID'),
                'method': form.get('method', 'No Method'),
                'action': form.get('action', 'No Action')
            }
            page_info['forms'].append(form_info)
            
        # Find major content sections
        for section in soup.find_all(['section', 'main', 'article']):
            section_info = {
                'type': section.name,
                'id': section.get('id', 'No ID'),
                'class': section.get('class', 'No Class')
            }
            page_info['major_sections'].append(section_info)
            
        return page_info
    
    @staticmethod
    def parse_date_time(date_text: str) -> Tuple[str, str]:
        """
        Parse date and time from news row
        
        Args:
            date_text: Text containing date/time information
            
        Returns:
            Tuple of (date, time)
        """
        date_data = date_text.strip().split()
        
        if len(date_data) == 1:  # Only time is provided
            time = date_data[0]
            date = datetime.today().strftime('%Y-%m-%d')
        else:
            date = date_data[0]
            time = date_data[1]
            
        return date, time

    def get_stock_news(
        self,
        symbol: str,
        max_articles: int = 5,
        days_back: int = 7
    ) -> List[NewsArticle]:
        """
        Fetch recent news articles about the stock and analyze their sentiment
        
        Args:
            symbol: Stock ticker symbol
            max_articles: Maximum number of articles to return
            days_back: How many days back to look for news
            
        Returns:
            List of NewsArticle objects with sentiment scores
        """
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get page structure information
            page_info = self.inspect_page_content(soup)
            logging.debug(f"Page structure: {page_info}")
            
            news_table = soup.find(id='news-table')
            if not news_table:
                logging.warning(f"No news table found for symbol {symbol}")
                return []
                
            news_rows = news_table.findAll('tr')
            if not news_rows:
                logging.warning(f"No news rows found for symbol {symbol}")
                return []
            
            news_list = []
            for row in news_rows:
                try:
                    title_element = row.find('a')
                    if not title_element:
                        continue
                        
                    date_element = row.find('td', {'align': 'right'})
                    if not date_element:
                        continue
                        
                    date, time = self.parse_date_time(date_element.text)
                    title = title_element.text.strip()
                    
                    # Get sentiment for the title
                    sentiment_score, sentiment_label = self.analyze_sentiment(title)
                    
                    article = NewsArticle(
                        title=title,
                        date=date,
                        time=time,
                        source=row.find('span').text.strip() if row.find('span') else "Unknown",
                        url=title_element['href'] if title_element else None,
                        sentiment_score=sentiment_score,
                        sentiment_label=sentiment_label
                    )
                    
                    news_list.append(article)
                    
                    if len(news_list) >= max_articles:
                        break
                        
                except Exception as e:
                    logging.error(f"Error parsing news row: {str(e)}")
                    continue
                    
            return news_list
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching news for {symbol}: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error processing news for {symbol}: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text using FinBERT model
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        if not self.sentiment_analyzer:
            return (0.0, "neutral")
            
        try:
            # Get sentiment prediction
            result = self.sentiment_analyzer(text)[0]
            label = result['label']
            score = result['score']
            
            # Convert score to range [-1, 1] based on label
            if label == "positive":
                final_score = score
            elif label == "negative":
                final_score = -score
            else:
                final_score = 0.0
                
            return (final_score, label)
            
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {str(e)}")
            return (0.0, "neutral")

    def get_aggregate_sentiment(self, articles: List[NewsArticle]) -> Dict:
        """
        Calculate aggregate sentiment statistics from articles
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            Dictionary with sentiment statistics
        """
        if not articles:
            return {
                'average_score': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'confidence': 0.0
            }
            
        scores = [article.sentiment_score for article in articles if article.sentiment_score is not None]
        labels = [article.sentiment_label for article in articles if article.sentiment_label is not None]
        
        sentiment_dist = {
            'positive': labels.count('positive'),
            'neutral': labels.count('neutral'),
            'negative': labels.count('negative')
        }
        
        return {
            'average_score': np.mean(scores) if scores else 0.0,
            'sentiment_distribution': sentiment_dist,
            'confidence': np.std(scores) if len(scores) > 1 else 0.0
        }