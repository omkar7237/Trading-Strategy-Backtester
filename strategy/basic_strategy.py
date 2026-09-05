import pandas as pd

def generate_signals(data, fast_period=20, slow_period=50):

    signals = pd.Series(
        0,
        index = data.index,
        name = "Signal"
    )

    fast_column = f"SMA_{fast_period}"
    slow_column = f"SMA_{slow_period}"
    
    buy_condition = (
        (data[fast_column]>data[slow_column]) &
        (data["RSI_14"] > 50) &
        (data["MACD"] > data["MACD_Signal"])
    )

    sell_condition = (
        (data[fast_column] < data[slow_column]) 
        |
        (data["MACD"] < data["MACD_Signal"])
    )

    signals[buy_condition] = 1
    signals[sell_condition] = -1

    return signals