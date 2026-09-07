import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from data.loader import load_data

from data.indicator import (
    sma,
    ema
)

from strategy.moving_average_strategy import (
    MovingAverageStrategy
)

data = load_data(
    "AAPL"
)

data["SMA_20"] = sma(
    data,
    20
)

data["SMA_50"] = sma(
    data,
    50
)

strategy = MovingAverageStrategy(
    short_window=20,
    long_window=50
)

data["Signal"] = strategy.generate_signals(
    data
)

print(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
            "Signal"
        ]
    ].tail(20)
)