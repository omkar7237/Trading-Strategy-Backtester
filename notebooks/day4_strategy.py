import sys
from pathlib import Path
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma,ema,rsi,macd,bollinger_bands
from strategy.basic_strategy import generate_signals

data = load_data("AAPL")

data["SMA_20"] = sma(data,20)
data["SMA_50"] = sma(data,50)

data["EMA_20"] = ema(data,20)

data["RSI_14"] = rsi(data)

data["MACD"],data["MACD_Signal"],data["MACD_Hist"] = macd(data)

data["BB_Upper"],data["BB_Middle"], data["BB_Lower"] = bollinger_bands(data)

data["Signal"] = generate_signals(data)

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
                "Signal"
            ]
    ].tail(30)
)

print("\nSignal Counts:")
print(data["Signal"].value_counts())

print("\nSignal Percentages:")
print(
    data["Signal"]
    .value_counts(normalize=True)
    .mul(100)
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x = data.index,
        y = data["Close"],
        mode="lines",
        name = "AAPL"
    )
    
)

buy_points = data[data["Signal"] == 1]
sell_points = data[data["Signal"] == -1]

fig.add_trace(
    go.Scatter(
        x = buy_points.index,
        y = buy_points["Close"],
        mode = "markers",
        name = "BUY"
    )
)

fig.add_trace(
    go.Scatter(
        x = sell_points.index,
        y = sell_points["Close"],
        mode = "markers",
        name = "SELL"
    )
)

fig.update_layout(
    title = "AAPL Strategy Signals",
    xaxis_title = "Date",
    yaxis_title = "Price"
)

fig.show()
