import pandas as pd

def sma(data,period):

    #simple moving average

    return data["Close"].rolling(
        window=period
    ).mean()

def ema(data,period):

    #exponential moving average

    return data["Close"].ewm(
        span = period,
        adjust = False
    ).mean()

def rsi(data,period=14):

    delta = data["Close"].diff()

    gain = delta.clip(lower = 0)
    loss = -delta.clip(upper = 0)

    average_gain = gain.ewm(
        alpha=1/period,
        adjust = False
    ).mean()

    average_loss = loss.ewm(
        alpha=1/period,
        adjust = False
    ).mean()

    rs = average_gain / average_loss

    return 100 - (100/(1+rs))

def macd(data):

    ema_12 = data["Close"].ewm(
        span = 12,
        adjust = False
    ).mean()

    ema_26 = data["Close"].ewm(
        span = 26,
        adjust = False
    ).mean()

    macd_line = ema_12 - ema_26

    signal_line = macd_line.ewm(
        span = 9,
        adjust = False
    ).mean()

    histogram = macd_line - signal_line

    return macd_line,signal_line,histogram

def bollinger_bands(data,period = 20, std_dev=2):

    middle = data["Close"].rolling(
        window=period
    ).mean()

    std = data["Close"].rolling(
        window=period
    ).std()

    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)

    return upper, middle, lower