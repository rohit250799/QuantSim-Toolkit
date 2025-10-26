import pandas as pd

from returns_analyzer import calculate_daily_returns_from_hardcoded_list

def calculate_portfolio_returns(df_prices: pd.DataFrame) -> pd.Series:
    """
    Used to calculate the portfolio returns - for all stocks contained in the portfolio

    Args:
    df_prices (pandas DataFrame) - A pandas dataframe where the index is a Datetimeindex and each column represents a single asset
    with each value in the column representing the daily closing price for that asset on that date

    Returns:
    A Pandas series representing the daily return of the portfolio with a datetimeindex
    """
    daily_returns_dataframe: pd.Series = calculate_daily_returns_from_hardcoded_list(df_prices)
    return daily_returns_dataframe


df_test = pd.DataFrame({
    'TCS': [100.0, 102.0, 101.0, 105.0, 104.0],
    'INFY': [200.0, 198.0, 202.0, 205.0, 208.0],
    'RELIANCE': [150.0, 152.0, 149.0, 155.0, 158.0]
}, index=pd.date_range(start='2024-01-01', periods=5, freq='D'))


result = calculate_portfolio_returns(df_prices=df_test)
print(result)