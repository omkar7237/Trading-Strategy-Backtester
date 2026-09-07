import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma, ema, rsi, macd, bollinger_bands
from strategy.basic_strategy import generate_signals
from backtest.engine import BacktestEngine


from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI(
    title="Trading Strategy Backtester API",
    description="API for running trading strategy backtests",
    version="1.0.0"
)


class BacktestRequest(BaseModel):

    symbol: str = "AAPL"

    initial_capital: float = 10000

    commission: float = 0.001

    slippage: float = 0

    position_size: float = 0.5

    short_window: int = 20

    long_window: int = 50


def run_backtest(request: BacktestRequest):

    data = load_data(request.symbol)

    data["SMA_20"] = sma(data, request.short_window)

    data["SMA_50"] = sma(data, request.long_window)

    data["EMA_20"] = ema(data, 20)

    data["RSI_14"] = rsi(data)

    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
        bollinger_bands(data)
    )

    data["Signal"] = generate_signals(data)

    engine = BacktestEngine(
        initial_capital=request.initial_capital,
        commission=request.commission,
        slippage=request.slippage,
        position_size=request.position_size
    )

    portfolio_values = []

    for i in range(len(data) - 1):

        next_date = data.index[i + 1]

        signal = data["Signal"].iloc[i]

        next_open = data["Open"].iloc[i + 1]

        if signal == 1:

            engine.buy(
                next_date,
                next_open
            )

        elif signal == -1:

            engine.sell(
                next_date,
                next_open
            )

        value = engine.portfolio_value(next_open)

        portfolio_values.append(value)

    final_price = data["Close"].iloc[-1]

    final_value = engine.portfolio_value(final_price)

    return final_value


@app.get("/")
def root():

    return {
        "message": "Trading Strategy Backtester API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/backtest")
def backtest(request: BacktestRequest):

    final_value = run_backtest(request)

    total_return = (
        (final_value - request.initial_capital)
        / request.initial_capital
    ) * 100

    buy_hold_shares = int(
        request.initial_capital // data["Open"].iloc[0]
    )

    buy_hold_cash = (
        request.initial_capital
        - buy_hold_shares * data["Open"].iloc[0]
    )

    buy_hold_value = (
        buy_hold_cash
        + buy_hold_shares * data["Close"].iloc[-1]
    )

    buy_hold_return = (
    (buy_hold_value - request.initial_capital)
    / request.initial_capital
    ) * 100

    return {
        "symbol": request.symbol,
        "initial_capital": request.initial_capital,
        "final_value": final_value,
        "total_return": total_return,
        "Buy and hold" : buy_hold_value,
        "B&H return" : buy_hold_return
    }