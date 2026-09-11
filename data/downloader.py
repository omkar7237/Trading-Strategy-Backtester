import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import os
import requests
from typing import Optional


def download_data(symbol, start, end):

    data = yf.download(
        symbol,
        start=start,
        end=end,
        auto_adjust=True
    )

    # Flatten yfinance MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Keep only required columns
    data = data[
        [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ]

    # Make sure dates are sorted
    data = data.sort_index()

    return data


class NewsDownloader:
    """
    Downloads news articles for a given ticker using NewsAPI or GDELT.
    Stores news in data/raw/news/{ticker}_news.csv
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NewsDownloader.
        
        Args:
            api_key: NewsAPI key. Falls back to NEWS_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.news_dir = Path("data/raw/news")
        self.news_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_news_newsapi(self, ticker: str, days: int = 90) -> list:
        """
        Fetch news from NewsAPI for the given ticker.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of news to fetch (default 90)
            
        Returns:
            List of news articles as dicts
        """
        if not self.api_key:
            raise ValueError("NewsAPI key not provided. Set NEWS_API_KEY env var or pass api_key.")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        articles = []
        url = "https://newsapi.org/v2/everything"
        
        # Search for company name and ticker
        query = f'"{ticker}" OR "{ticker} stock" OR "{ticker} shares"'
        
        # NewsAPI has pagination limit of 100 results per request
        page = 1
        while True:
            params = {
                "q": query,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key,
                "page": page,
                "pageSize": 100
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "ok":
                    print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                    break
                    
                batch = data.get("articles", [])
                if not batch:
                    break
                    
                articles.extend(batch)
                
                # Stop if we got less than pageSize (no more pages)
                if len(batch) < 100:
                    break
                    
                page += 1
                
                # Safety limit to avoid too many API calls
                if page > 5:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching news: {e}")
                break
        
        return articles
    
    def fetch_news_gdelt(self, ticker: str, days: int = 90) -> list:
        """
        Fetch news from GDELT (free, no API key required).
        Uses GDELT's CSV export feature.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of news to fetch
            
        Returns:
            List of news articles as dicts
        """
        # GDELT approach: Use their search API or direct CSV downloads
        # This is a simplified version - in production you'd use GDELT's full API
        articles = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # GDELT doesn't have a simple REST API for this, so we simulate
        # In production, you would integrate with GDELT's BigQuery or CSV exports
        print(f"GDELT integration: Would fetch news for {ticker} from {start_date} to {end_date}")
        print("Note: Full GDELT integration requires BigQuery access or CSV parsing.")
        
        return articles
    
    def parse_articles(self, articles: list, ticker: str) -> pd.DataFrame:
        """
        Parse raw articles into DataFrame with required columns.
        
        Args:
            articles: List of article dicts from API
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with columns: date, headline, summary, source, sentiment_score
        """
        if not articles:
            return pd.DataFrame(columns=["date", "headline", "summary", "source", "sentiment_score"])
        
        parsed = []
        for article in articles:
            # Handle different API response formats
            published_at = article.get("publishedAt") or article.get("published_date")
            if not published_at:
                continue
                
            try:
                date = pd.to_datetime(published_at).tz_localize(None)
            except Exception:
                continue
            
            parsed.append({
                "date": date,
                "headline": article.get("title", "")[:500],  # Truncate very long titles
                "summary": article.get("description", "")[:1000] if article.get("description") else "",
                "source": article.get("source", {}).get("name", article.get("source", "Unknown")),
                "sentiment_score": 0.0  # Placeholder, will be filled by sentiment analysis
            })
        
        df = pd.DataFrame(parsed)
        if not df.empty:
            df = df.drop_duplicates(subset=["headline"])
            df = df.sort_values("date").reset_index(drop=True)
        
        return df
    
    def download_news(self, ticker: str, days: int = 90, use_gdelt: bool = False) -> pd.DataFrame:
        """
        Download news for a ticker and save to CSV.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of news to fetch
            use_gdelt: If True, use GDELT instead of NewsAPI
            
        Returns:
            DataFrame with news articles
        """
        if use_gdelt or not self.api_key:
            articles = self.fetch_news_gdelt(ticker, days)
        else:
            articles = self.fetch_news_newsapi(ticker, days)
        
        df = self.parse_articles(articles, ticker)
        
        # Save to CSV
        output_path = self.news_dir / f"{ticker}_news.csv"
        df.to_csv(output_path, index=False)
        
        print(f"Saved {len(df)} news articles to {output_path}")
        
        return df
    
    def load_cached_news(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Load previously downloaded news from cache.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with news articles, or None if not found
        """
        path = self.news_dir / f"{ticker}_news.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path, parse_dates=["date"])
        return df


if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    downloader = NewsDownloader()
    
    for symbol in symbols:
        print(f"\nDownloading news for {symbol}...")
        try:
            news_df = downloader.download_news(symbol, days=90)
            print(f"Found {len(news_df)} articles")
            if not news_df.empty:
                print(news_df.head())
        except Exception as e:
            print(f"Error downloading news for {symbol}: {e}")