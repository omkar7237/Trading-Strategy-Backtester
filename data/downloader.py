import yfinance as yf
import pandas as pd
from pathlib import Path

def download_data(symbol, start, end):
    data = yf.download(
        symbol,
        start = start,
        end = end,
        auto_adjust = True
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data

if __name__ == "__main__":

    symbol = "MSFT"

    data = download_data(
        symbol,
        "2020-01-01",
        "2025-01-01"
    )

    output_path = Path(f"data/raw/{symbol}.csv")
    data.to_csv(output_path)

    print(f"Saved data to {output_path}")
    print(f"Rows: {len(data)}")