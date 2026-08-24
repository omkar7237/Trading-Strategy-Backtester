import pandas as pd

def generate_signals(data):

    signals = pd.Series(
        0,
        index = data.index,
        name = "Signal"
    )

    buy_condition = (
        (data["SMA_20"]>data["SMA_50"]) &
        (data["RSI_14"] > 50) &
        (data["MACD"] > data["MACD_Signal"])
    )

    sell_condition = (
        (data["SMA_20"]<data["SMA_50"]) &
        (data["RSI_14"] < 50) &
        (data["MACD"] < data["MACD_Signal"])
    )

    signals[buy_condition] = 1
    signals[sell_condition] = -1

    return signals