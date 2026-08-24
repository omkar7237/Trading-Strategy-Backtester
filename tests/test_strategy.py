import pandas as pd

from strategy.basic_strategy import generate_signals


def test_buy_signal():

    data = pd.DataFrame({
        "SMA_20": [110],
        "SMA_50": [100],
        "RSI_14": [60],
        "MACD": [5],
        "MACD_Signal": [3]
    })

    signal = generate_signals(data)

    assert signal.iloc[0] == 1


def test_sell_signal():

    data = pd.DataFrame({
        "SMA_20": [90],
        "SMA_50": [100],
        "RSI_14": [40],
        "MACD": [-5],
        "MACD_Signal": [-3]
    })

    signal = generate_signals(data)

    assert signal.iloc[0] == -1


def test_hold_signal():

    data = pd.DataFrame({
        "SMA_20": [110],
        "SMA_50": [100],
        "RSI_14": [40],
        "MACD": [5],
        "MACD_Signal": [3]
    })

    signal = generate_signals(data)

    assert signal.iloc[0] == 0