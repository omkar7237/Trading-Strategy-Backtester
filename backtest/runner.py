import pandas as pd

from data.loader import load_data

from data.indicator import (
    sma,
    ema,
    rsi,
    macd,
    bollinger_bands
)

from strategy.basic_strategy import generate_signals

from backtest.engine import BacktestEngine


class BacktestRunner:

    def __init__(self, config):

        self.config = config


    def prepare_data(self):

        symbol = self.config["symbol"]

        data = load_data(symbol)

        data = data.copy()

        data["SMA_20"] = sma(
            data,
            self.config["short_window"]
        )

        data["SMA_50"] = sma(
            data,
            self.config["long_window"]
        )

        data["EMA_20"] = ema(
            data,
            20
        )

        data["RSI_14"] = rsi(
            data
        )

        (
            data["MACD"],
            data["MACD_Signal"],
            data["MACD_Hist"]
        ) = macd(data)

        (
            data["BB_Upper"],
            data["BB_Middle"],
            data["BB_Lower"]
        ) = bollinger_bands(data)

        data["Signal"] = generate_signals(
            data
        )

        return data


    def run(self):

        data = self.prepare_data()

        engine = BacktestEngine(
            initial_capital=self.config[
                "initial_capital"
            ],
            commission=self.config[
                "commission"
            ],
            slippage=self.config[
                "slippage"
            ],
            position_size=self.config[
                "position_size"
            ]
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

            value = engine.portfolio_value(
                next_open
            )

            portfolio_values.append({
                "Date": next_date,
                "Portfolio": value
            })

        portfolio = pd.DataFrame(
            portfolio_values
        )

        portfolio.set_index(
            "Date",
            inplace=True
        )

        final_price = data["Close"].iloc[-1]

        final_value = engine.portfolio_value(
            final_price
        )

        return {
            "data": data,
            "portfolio": portfolio,
            "engine": engine,
            "final_value": final_value
        }