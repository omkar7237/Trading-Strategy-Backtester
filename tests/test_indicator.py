from data.loader import load_data
from data.indicator import sma, ema, rsi


def test_sma():

    data = load_data("AAPL")

    result = sma(data, 20)

    assert len(result) == len(data)
    assert result.iloc[19] == result.iloc[19]


def test_ema():

    data = load_data("AAPL")

    result = ema(data, 20)

    assert len(result) == len(data)


def test_rsi():

    data = load_data("AAPL")

    result = rsi(data, 14)

    assert len(result) == len(data)
    assert result.dropna().between(0, 100).all()