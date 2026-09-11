"""
News sentiment analysis module.
Uses LLM (OpenAI/Ollama) to score political/market impact of news articles.
"""

import pandas as pd
import os
from typing import Optional, Literal
from pathlib import Path
from datetime import datetime, timedelta


class NewsSentimentAnalyzer:
    """
    Analyzes sentiment of news articles using LLM.
    Supports OpenAI and Ollama backends.
    """
    
    def __init__(
        self, 
        provider: Literal["openai", "ollama"] = "ollama",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the sentiment analyzer.
        
        Args:
            provider: LLM provider ("openai" or "ollama")
            model: Model name. Defaults based on provider.
            api_key: API key for OpenAI (not needed for Ollama)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Default models
        if provider == "openai":
            self.model = model or "gpt-3.5-turbo"
        else:  # ollama
            self.model = model or "llama2"
        
        self._client = None
    
    def _get_client(self):
        """Lazy load the LLM client."""
        if self._client is not None:
            return self._client
        
        if self.provider == "openai":
            try:
                from openai import OpenAI
                if not self.api_key:
                    raise ValueError("OpenAI API key required")
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Install openai package: pip install openai")
        else:  # ollama
            try:
                import ollama
                self._client = ollama
            except ImportError:
                raise ImportError("Install ollama package: pip install ollama")
        
        return self._client
    
    def _analyze_single_sentiment(self, headline: str, summary: str = "") -> float:
        """
        Analyze sentiment of a single news article.
        
        Args:
            headline: Article headline
            summary: Article summary/description
            
        Returns:
            Sentiment score between -1 (very negative) and +1 (very positive)
        """
        prompt = f"""
Analyze the following financial news article and provide a sentiment score.

HEADLINE: {headline}
SUMMARY: {summary}

Consider:
1. Market/stock price impact (positive/negative)
2. Political/regulatory implications
3. Company-specific news (earnings, products, scandals)

Respond with ONLY a number between -1 and +1 where:
- -1 = Very negative (scandals, losses, regulatory crackdowns)
- -0.5 = Negative (missed earnings, concerns)
- 0 = Neutral (routine announcements)
- +0.5 = Positive (good earnings, new products)
- +1 = Very positive (major breakthroughs, record profits)

Score:"""

        try:
            client = self._get_client()
            
            if self.provider == "openai":
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip()
            else:  # ollama
                response = client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response["message"]["content"].strip()
            
            # Parse the numeric result
            # Handle cases where LLM returns text around the number
            import re
            numbers = re.findall(r'-?\d+\.?\d*', result)
            if numbers:
                score = float(numbers[0])
                # Clamp to [-1, 1]
                return max(-1.0, min(1.0, score))
            else:
                return 0.0  # Default neutral if parsing fails
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def analyze_batch(
        self, 
        headlines: list[str], 
        summaries: list[str],
        show_progress: bool = True
    ) -> list[float]:
        """
        Analyze sentiment for multiple articles.
        
        Args:
            headlines: List of article headlines
            summaries: List of article summaries
            show_progress: Print progress updates
            
        Returns:
            List of sentiment scores
        """
        scores = []
        total = len(headlines)
        
        for i, (headline, summary) in enumerate(zip(headlines, summaries)):
            score = self._analyze_single_sentiment(headline, summary)
            scores.append(score)
            
            if show_progress and (i + 1) % 10 == 0:
                print(f"Analyzed {i + 1}/{total} articles...")
        
        return scores


def analyze_news_sentiment(
    ticker: str,
    start_date: str | datetime,
    end_date: str | datetime,
    provider: Literal["openai", "ollama"] = "ollama",
    model: Optional[str] = None,
    use_cached: bool = True
) -> pd.DataFrame:
    """
    Analyze sentiment for news articles within a date range.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date for analysis
        end_date: End date for analysis
        provider: LLM provider ("openai" or "ollama")
        model: Model name
        use_cached: Use cached news if available
        
    Returns:
        DataFrame with columns: date, headline, summary, source, sentiment_score
        Aligned with trading dates (forward-filled for missing dates)
    """
    from data.downloader import NewsDownloader
    
    # Convert string dates to datetime
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    # Load or download news
    downloader = NewsDownloader()
    
    if use_cached:
        news_df = downloader.load_cached_news(ticker)
    
    if not use_cached or news_df is None or news_df.empty:
        print(f"Downloading news for {ticker}...")
        news_df = downloader.download_news(ticker, days=90)
    
    if news_df is None or news_df.empty:
        print(f"No news found for {ticker}")
        return pd.DataFrame(columns=["date", "headline", "summary", "source", "sentiment_score"])
    
    # Filter by date range
    news_df = news_df[
        (news_df["date"] >= start_date) & 
        (news_df["date"] <= end_date)
    ].copy()
    
    if news_df.empty:
        print(f"No news in date range {start_date} to {end_date}")
        return pd.DataFrame(columns=["date", "headline", "summary", "source", "sentiment_score"])
    
    # Check which articles need sentiment analysis
    needs_analysis = news_df["sentiment_score"] == 0.0
    
    if needs_analysis.any():
        print(f"Analyzing sentiment for {needs_analysis.sum()} articles...")
        
        analyzer = NewsSentimentAnalyzer(provider=provider, model=model)
        
        headlines_to_analyze = news_df.loc[needs_analysis, "headline"].tolist()
        summaries_to_analyze = news_df.loc[needs_analysis, "summary"].tolist()
        
        scores = analyzer.analyze_batch(headlines_to_analyze, summaries_to_analyze)
        
        # Update scores
        news_df.loc[needs_analysis, "sentiment_score"] = scores
        
        # Save updated news with sentiment
        output_path = Path("data/raw/news") / f"{ticker}_news.csv"
        news_df.to_csv(output_path, index=False)
        print(f"Saved updated news with sentiment to {output_path}")
    
    return news_df


def merge_sentiment_with_ohlcv(
    ohlcv_df: pd.DataFrame,
    news_df: pd.DataFrame,
    fill_method: Literal["ffill", "mean", "zero"] = "ffill"
) -> pd.DataFrame:
    """
    Merge OHLCV price data with news sentiment.
    
    Args:
        ohlcv_df: DataFrame with OHLCV data (index must be DatetimeIndex)
        news_df: DataFrame with news sentiment data
        fill_method: How to handle dates without news
            - "ffill": Forward fill last known sentiment
            - "mean": Fill with mean sentiment
            - "zero": Fill with 0 (neutral)
            
    Returns:
        DataFrame with OHLCV + sentiment_score column
    """
    if ohlcv_df.empty:
        return ohlcv_df.copy()
    
    # Ensure index is datetime
    if not isinstance(ohlcv_df.index, pd.DatetimeIndex):
        ohlcv_df = ohlcv_df.copy()
        ohlcv_df.index = pd.to_datetime(ohlcv_df.index)
    
    if news_df is None or news_df.empty:
        # No news, add zero sentiment
        result = ohlcv_df.copy()
        result["sentiment_score"] = 0.0
        return result
    
    # Ensure news dates are datetime
    news_df = news_df.copy()
    news_df["date"] = pd.to_datetime(news_df["date"])
    news_df = news_df.set_index("date")
    
    # Resample news to daily, taking mean sentiment for each day
    daily_sentiment = news_df["sentiment_score"].resample("D").mean()
    
    # Align with OHLCV dates
    result = ohlcv_df.copy()
    result["sentiment_score"] = daily_sentiment.reindex(result.index.date).values
    
    # Handle missing dates
    if fill_method == "ffill":
        result["sentiment_score"] = result["sentiment_score"].ffill().fillna(0.0)
    elif fill_method == "mean":
        mean_sent = result["sentiment_score"].mean()
        result["sentiment_score"] = result["sentiment_score"].fillna(mean_sent)
    else:  # zero
        result["sentiment_score"] = result["sentiment_score"].fillna(0.0)
    
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    print(f"Analyzing sentiment for {ticker} from {start_date} to {end_date}")
    
    news_df = analyze_news_sentiment(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        provider="ollama"  # Use "openai" if you have an API key
    )
    
    if not news_df.empty:
        print(f"\nAnalyzed {len(news_df)} articles")
        print("\nSample sentiment scores:")
        print(news_df[["date", "headline", "sentiment_score"]].head(10))
        
        # Show sentiment distribution
        print(f"\nSentiment statistics:")
        print(news_df["sentiment_score"].describe())
