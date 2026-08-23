import sys
from pathlib import Path

import plotly.graph_objects as go

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma, ema, rsi, macd,bollinger_bands


data = load_data("AAPL")

data["SMA_20"] = sma(data, 20)
data["SMA_50"] = sma(data, 50)

data["EMA_20"] = ema(data, 20)

data["RSI_14"] = rsi(data)

print(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
            "EMA_20"
        ]
    ].tail(20)
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x = data.index,
        y = data["Close"],
        mode = "lines",
        name = "AAPL"
    )
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y = data["SMA_20"],
        mode="lines",
        name="SMA 20"
    )
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["SMA_50"],
        mode = "lines",
        name = "SMA 50"
    )
)

fig.update_layout(
    title = "AAPL Price with Moving Averages",
    xaxis_title = "Date",
    yaxis_title = "Price (USD)"
)

fig.show()


data["Trend"] = 0

data.loc[
    data["SMA_20"] > data["SMA_50"],
    "Trend"
] = 1

data.loc[
    data["SMA_20"] < data["SMA_50"],
    "Trend"
] = -1

'''
Trend =  1 → bullish
Trend = -1 → bearish
Trend =  0 → neutral
'''

print(data[["Close","RSI_14"]].tail(20))

data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

data["BB_Upper"],data["BB_Middle"],data["BB_Lower"] = bollinger_bands(data)

print(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
            "EMA_20",
            "RSI_14",
            "MACD",
            "MACD_Signal",
            "BB_Upper",
            "BB_Middle",
            "BB_Lower"
        ]
    ].tail(10)
)