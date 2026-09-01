import pandas as pd


class BacktestEngine:

    def __init__(
        self,
        initial_capital=10000,
        commission=0.001,
        slippage=0.001,
        position_size = 1.0,
        stop_loss = None,
        take_profit = None
    ):

        self.initial_capital = initial_capital

        self.cash = initial_capital

        self.position = 0

        self.entry_price = 0

        self.trades = []

        self.commission = commission

        self.slippage = slippage

        self.position_size = position_size

        self.stop_loss = stop_loss

        self.take_profit = take_profit

    def buy(self, date, price):

        if self.position > 0:
            return

        # Slippage makes buying more expensive
        execution_price = price * (1 + self.slippage)

        self.stop_price = None
        self.target_price = None

        if self.stop_loss is not None:
            self.stop_price = price * (1 - self.stop_loss)

        if self.take_profit is not None:
            self.target_price = price * (1 + self.take_profit)

        capital_to_use = self.cash * self.position_size

        shares = int(
            capital_to_use // (
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

    def check_risk_exit(self, date, price):

        if self.position <= 0:
            return False

        if (
            self.stop_price is not None
            and price <= self.stop_price
        ):
            self.sell(date, price)
            return True

        if (
            self.target_price is not None
            and price >= self.target_price
        ):
            self.sell(date, price)
            return True

        return False

            
                