import pandas as pd


class Portfolio:

    def __init__(
        self,
        initial_capital=10000
    ):

        self.initial_capital = initial_capital

        self.cash = initial_capital

        self.positions = {}

        self.trades = []


    def buy(
        self,
        symbol,
        date,
        price,
        amount
    ):

        if amount <= 0:
            return

        if amount > self.cash:
            amount = self.cash

        shares = int(
            amount // price
        )

        if shares <= 0:
            return

        cost = shares * price

        self.cash -= cost

        if symbol not in self.positions:

            self.positions[symbol] = 0

        self.positions[symbol] += shares

        self.trades.append({

            "Date": date,

            "Symbol": symbol,

            "Type": "BUY",

            "Price": price,

            "Shares": shares

        })


    def sell(
        self,
        symbol,
        date,
        price
    ):

        if symbol not in self.positions:
            return

        shares = self.positions[symbol]

        if shares <= 0:
            return

        proceeds = shares * price

        self.cash += proceeds

        self.positions[symbol] = 0

        self.trades.append({

            "Date": date,

            "Symbol": symbol,

            "Type": "SELL",

            "Price": price,

            "Shares": shares

        })


    def value(
        self,
        prices
    ):

        total = self.cash

        for symbol, shares in self.positions.items():

            if symbol in prices:

                total += (
                    shares * prices[symbol]
                )

        return total


    def get_trades(self):

        return pd.DataFrame(
            self.trades
        )