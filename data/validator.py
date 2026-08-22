def validate_data(data):

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    # Check required columns
    for column in required_columns:

        if column not in data.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    # Check for empty dataset
    if data.empty:
        raise ValueError(
            "Dataset is empty"
        )

    # Check date ordering
    if not data.index.is_monotonic_increasing:
        raise ValueError(
            "Data is not sorted by date"
        )

    # Check duplicate dates
    if data.index.duplicated().any():
        raise ValueError(
            "Duplicate dates found"
        )

    # Check missing values
    if data[required_columns].isnull().any().any():
        raise ValueError(
            "Missing values found in market data"
        )

    # Check OHLC relationships
    if (data["High"] < data["Low"]).any():
        raise ValueError(
            "High price is lower than Low price"
        )

    if (data["Close"] > data["High"]).any():
        raise ValueError(
            "Close price is higher than High price"
        )

    if (data["Close"] < data["Low"]).any():
        raise ValueError(
            "Close price is lower than Low price"
        )

    # Check negative prices
    price_columns = [
        "Open",
        "High",
        "Low",
        "Close"
    ]

    if (data[price_columns] <= 0).any().any():
        raise ValueError(
            "Zero or negative prices found"
        )

    return True