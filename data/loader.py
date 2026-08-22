import pandas as pd
from pathlib import Path


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