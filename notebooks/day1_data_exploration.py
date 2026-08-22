import pandas as pd
import plotly.graph_objects as go

data = pd.read_csv(
    "data/raw/AAPL.csv",
    index_col=0
)

#convert columns to numeric
price_columns = ["Close","High","Low","Open"]

for column in price_columns:
    data[column] = pd.to_numeric(data[column], errors="coerce")

#basic info
print(data.head())
print("\nData types:")
print(data.dtypes)

print("\nData Shape:")
print(data.shape)

print("\nColumns:")
print(data.columns)

print("\nData Types:")
print(data.dtypes)

print("\nMissing Values:")
print(data.isnull().sum())

print("\nBasic Statistics:")
print(data.describe())

#calculate daily returns
data["Return"] = data["Close"].pct_change(fill_method=None)

print("\nDaily Returns:")
print(data[["Close","Return"]].head(10))

#calculate cumulative returns
data["Cumulative Return"] = (
    1 + data["Return"]
).cumprod() - 1

print("\nCumulative Returns:")
print(data[["Close","Return","Cumulative Return"]].tail())

best_day = data["Return"].idxmax()
worst_day = data["Return"].idxmin()

print("\nBest Trading Day:")
print(best_day, data.loc[best_day])

print("\nWorst Trading Day:")
print(worst_day, data.loc[worst_day])

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x = data.index,
        y = data["Close"],
        mode = "lines",
        name = "AAPL"
    )
)

fig.update_layout(
    title = "AAPL Historical Price",
    xaxis_title = "Date",
    yaxis_title = "Price (USD)"
)

fig.show()

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Cumulative Return"]*100,
        mode = "lines",
        name = "Cumulative Returns"
    )
)

fig.update_layout(
    title = "AAPL Cumulative Returns",
    xaxis_title = "Date",
    yaxis_title = "Cumulative Returns (%)"
)

fig.show()