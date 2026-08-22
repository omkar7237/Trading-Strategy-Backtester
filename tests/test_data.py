from data.loader import load_data
from data.validator import validate_data


data = load_data("AAPL")

validate_data(data)

print(data.head(10))