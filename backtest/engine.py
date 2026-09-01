import pandas as pd


class BacktestEngine:

    def __init__(
        self,
        initial_capital=10000,
        commission=0.001,
        slippage=0.001
    ):

        self.initial_capital = initial_capital

        self.cash = initial_capital

        self.position = 0

        self.entry_price = 0

        self.trades = []

        self.commission = commission

        self.slippage = slippage

    def buy(self, date, price):

        if self.position > 0:
            return

        # Slippage makes buying more expensive
        execution_price = price * (1 + self.slippage)

        shares = int(
            self.cash // (
                execution_price * (1 + self.commission)
            )
        )

        if shares <= 0:
            return

        trade_value = shares * execution_price

        commission_cost = (
            trade_value * self.commission
        )

        total_cost = (
            trade_value + commission_cost
        )

        self.cash -= total_cost

        self.position = shares

        self.entry_price = execution_price

        self.trades.append({
            "Date": date,
            "Type": "BUY",
            "Price": execution_price,
            "Shares": shares,
            "Commission": commission_cost
        })

    def sell(self, date, price):        

        if self.position <= 0:
            return

        shares = self.position

        # Slippage makes selling slightly worse
        execution_price = price * (1 - self.slippage)

        trade_value = (
            shares * execution_price
        )

        commission_cost = (
            trade_value * self.commission
        )

        proceeds = (
            trade_value - commission_cost
        )

        self.cash += proceeds

        self.trades.append({
            "Date": date,
            "Type": "SELL",
            "Price": execution_price,
            "Shares": shares,
            "Commission": commission_cost
        })

        self.position = 0

        self.entry_price = 0

    def portfolio_value(self,price):
        return self.cash + (self.position * price)

    def get_trades(self):
        return pd.DataFrame(self.trades)

            
                