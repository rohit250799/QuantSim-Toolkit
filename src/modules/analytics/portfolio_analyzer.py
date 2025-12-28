import logging
import pandas as pd
import matplotlib.pyplot as plt

from src.modules.analytics.returns_analyzer import calculate_daily_portfolio_returns, read_all_csv_data

logger = logging.getLogger("analytics")


def calculate_portfolio_returns(df_prices: pd.DataFrame) -> pd.Series: 
    """
    Used to calculate the portfolio returns - for all stocks contained in the portfolio

    Args:
    df_prices (pandas DataFrame) - A pandas dataframe where the index is a Datetimeindex and each column represents a single asset
    with each value in the column representing the daily closing price for that asset on that date

    Returns:
    A Pandas series representing the daily return of the portfolio with a datetimeindex
    """
    daily_returns_dataframe: pd.Series = calculate_daily_portfolio_returns(df_test)
    print(type(daily_returns_dataframe))
    return daily_returns_dataframe

def plot_cumulative_returns(df_prices: pd.DataFrame) -> None:
    """
    Used to plot the cumulative returns of the entire portfolio vs individual stocks in the portfolio over a period of time

    Args: 
    df_prices(Pandas dataframe) - Stores the data about daily closing prices of stocks as list and stock symbols as columns

    Returns:
    A line chart plotting the individual asset returns against the average portfolio returns over a period of time. The line chart is shown
    in the terminal and also gets saved inside the plots/ directory as a png image for any future reference. 
    """
    dataframe_individual_asset_returns = df_prices.pct_change()
    portfolio_returns = calculate_portfolio_returns(df_prices=df_test)

    cumulative_returns_for_each_asset = (1 + dataframe_individual_asset_returns).cumprod()
    cumulative_returns_for_portfolio = (1 + portfolio_returns).cumprod()

    plt.figure(figsize=(14, 8))
    plt.title(label='Cumulative Returns: Portfolio vs Individual Assets')

    cumulative_returns_for_each_asset.plot(ax=plt.gca(), linewidth=1.5, alpha=0.7)
    cumulative_returns_for_portfolio.plot(ax=plt.gca(), linewidth=3, color='black', label='Equally weighted portfolio')
    
    plt.xlabel(xlabel='Date')
    plt.ylabel(ylabel='Cumulative Return: Growth of INR 1')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('QuantSim-Toolkit/plots/cumulative_returns.png', dpi=150, bbox_inches='tight')

    return plt.show()

df_test = pd.DataFrame({
    'TCS': [100.0, 102.0, 101.0, 105.0, 104.0],
    'INFY': [200.0, 198.0, 202.0, 205.0, 208.0],
    'RELIANCE': [150.0, 152.0, 149.0, 155.0, 158.0]
}, index=pd.date_range(start='2024-01-01', periods=5, freq='D'))

# result = plot_cumulative_returns(df_test)
# print(result)
# return
