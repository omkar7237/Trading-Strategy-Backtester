import pandas as pd

class BacktestEngine:
    def __init__(self,initial_capital=10000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []

    def buy(self,date,price):
        if self.position > 0:
            return

        shares = int(self.cash//price)

        if(shares <=0):
            return

        cost = shares * price

        self.cash -=cost

        self.position = shares

        self.entry_price = price

        self.trades.append(
            {
                "Date" : date,
                "Type" : "BUY",
                "Price" : price,
                "Shares" : shares
            }
        )

    def sell(self, date, price):

        if self.position <= 0:
            return

        shares = self.position

        proceeds = self.position * price

        self.cash += proceeds

        self.trades.append({
            "Date": date,
            "Type": "SELL",
            "Price": price,
            "Shares": self.position
        })

        self.position = 0

        self.entry_price = 0

    def portfolio_value(self,price):
        return self.cash + (self.position * price)

    def get_trades(self):
        return pd.DataFrame(self.trades)

            
                