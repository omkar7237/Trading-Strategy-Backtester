import pandas as pd
import yfinance as yf
from pathlib import Path


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


if __name__ == "__main__":

    symbols = [
        "AAPL",
        "MSFT",
        "GOOGL"
    ]

    start = "2020-01-01"
    end = "2025-01-01"

    for symbol in symbols:

        print(f"\nDownloading {symbol}...")

        data = download_data(
            symbol,
            start,
            end
        )

        output_path = Path(
            f"data/raw/{symbol}.csv"
        )

        data.to_csv(output_path)

        print(f"Saved: {output_path}")
        print(f"Rows: {len(data)}")
        print(f"Columns: {data.columns.tolist()}")