import pandas as pd
from pathlib import Path
from typing import Optional, Literal


def load_data(symbol):

    path = Path(
        f"data/raw/{symbol}.csv"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    data = pd.read_csv(
        path,
        index_col=0,
        parse_dates=True
    )

    # Make sure dates are sorted
    data = data.sort_index()

    return data


def load_enriched_data(
    ticker: str, 
    fill_method: Literal["ffill", "mean", "zero"] = "ffill"
) -> pd.DataFrame:
    """
    Load OHLCV data merged with news sentiment for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        fill_method: How to handle missing news dates
            - "ffill": Forward fill last known sentiment (default)
            - "mean": Fill with mean sentiment
            - "zero": Fill with 0 (neutral)
    
    Returns:
        DataFrame with OHLCV columns + sentiment_score
    """
    from data.loader import load_data
    from data.news_processor import merge_sentiment_with_ohlcv
    
    # Load OHLCV data
    ohlcv_df = load_data(ticker)
    
    # Load cached news
    news_path = Path(f"data/raw/news/{ticker}_news.csv")
    
    if not news_path.exists():
        print(f"No cached news found for {ticker}. Returning OHLCV only with zero sentiment.")
        ohlcv_df["sentiment_score"] = 0.0
        return ohlcv_df
    
    # Load news
    news_df = pd.read_csv(news_path, parse_dates=["date"])
    
    if news_df.empty:
        print(f"News file exists but is empty for {ticker}.")
        ohlcv_df["sentiment_score"] = 0.0
        return ohlcv_df
    
    # Merge OHLCV with sentiment
    enriched_df = merge_sentiment_with_ohlcv(
        ohlcv_df=ohlcv_df,
        news_df=news_df,
        fill_method=fill_method
    )
    
    return enriched_df


if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"Loading enriched data for {symbol}")
        print('='*50)
        
        try:
            df = load_enriched_data(symbol)
            print(f"Loaded {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            print("\nFirst few rows:")
            print(df.head())
            print("\nSentiment statistics:")
            print(df["sentiment_score"].describe())
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")