"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""
import logging
from collections.abc import Generator
from typing import Any, Dict, cast

import pandas as pd
import numpy as np

logger = logging.getLogger("analytics")

def get_stock_name() -> str:
    stock_name = input('Enter the stock name: ')
    return stock_name


def read_csv_stock_data_in_chunks(stock_symbol: str, chunksize: int = 10) -> Generator[Any, Any, Any]:
    """
    A generator to read stock data from the csv file in chunks and reorganises that in Series format with timestamp as index

    Args:
    stock_symbol: str - Symbol of the stock, since csv files are saved starting with their symbol name
    chunksize: int - size of the chunk in which the data is to be broken

    Returns:
    Pandas series with the timestamp values as the index and closing price of the stock as values
    """
    try:
        file_path: str = f'src/data/{stock_symbol}_id.csv'
    except FileNotFoundError:
        print('Invalid path! File not found there')
    else:
        df = pd.read_csv(file_path, usecols=['timestamp', 'close'], parse_dates=['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)

        date_range_index = pd.date_range(start=df['timestamp'].iloc[0], end=df['timestamp'].iloc[-1], freq='D')

        # Ensure date_range length matches the total rows (handle missing trading days if needed)
        if len(date_range_index) != len(df):
            df = df.set_index('timestamp').reindex(date_range_index).ffill().reset_index()
            df.columns = ['timestamp', 'close']

        for start_index in range(0, len(df), chunksize):
           end_index = start_index + chunksize
           chunk = df.iloc[start_index:end_index]
           series = pd.Series(data=chunk['close'].values, index=chunk['timestamp'])
           yield series

def read_all_csv_data(stock_symbol: str) -> pd.DataFrame:
    """
    Used to read data from a CSV file all at once

    Description:
    This function is used to read all data from a CSV file directly into memeory and is optimal to use in cases where the file size is smaller than
    memory (for smaller datasets) over generators 

    Args:
    stock_symbol(str) - A string representing the symbol of the stock that we want to analyze

    Returns:
    A Pandas dataframe with the timestamp column value of the stock csv file as index and the closing price column as value
    """
    try:
        file_path: str = f'src/data/{stock_symbol}_id.csv'
    except FileNotFoundError:
        print('Invalid path! File not found there')
        raise
    else:
        df = pd.read_csv(file_path, usecols=['timestamp', 'close'], dtype=np.float32,  parse_dates=['timestamp'], index_col=['timestamp'])
        df = df.sort_index()
        return df

def calculate_log_returns(df: pd.DataFrame):
    "Calculates the log returns of closing prices from the dataframe"
    price_columns = ['ticker_close', 'benchmark_close']
    return_cols = [col + '_log_return' for col in price_columns]
    df[return_cols] = np.log(df[price_columns] / df[price_columns].shift(1))
    logger.info('The updated dataframe with log returns is: \n%s', df)
    return

def calculate_cummulative_returns(df: pd.DataFrame):
    """Calculates and returns the commulative returns of the stock over the entire period"""
    ticker_initial_price = df['ticker_close'].iloc[0]
    ticker_final_price = df['ticker_close'].iloc[-1]

    benchmark_initial_point = df['benchmark_close'].iloc[0]
    benchmark_final_point = df['benchmark_close'].iloc[-1]

    ticker_cummulative_return = (ticker_final_price / ticker_initial_price - 1)
    benchmark_cummulative_return = (benchmark_final_point / benchmark_initial_point - 1)
    return (ticker_cummulative_return, benchmark_cummulative_return)

def calculate_volatility(df: pd.DataFrame):
    """
    Calculates the Standard Deviation of the ticker's daily returns and returns its annualized value
    """
    
    pass

#def 
    
# def perform_data_validation(df: pd.DataFrame) -> pd.Series:
#     """
#     All data validation is performed here and then the clean data is used for all the calculations and analysis
#     """

#     if "close" not in df.columns:
#         raise KeyError("Input DataFrame must contain a 'close' column")

#     cleaned = df.loc[
#         (df["close"] > 0)
#         & (df["close"].notna())
#         & (np.isfinite(df["close"]))
#     , "close"]

#     if cleaned.empty:
#         raise ArithmeticError("No valid closing prices available after filtering")

#     # Ensuring Series returned (not DataFrame)
#     cleaned = cleaned.astype(float)

#     return cast(pd.Series, cleaned)

# def calculate_daily_returns(close: pd.Series) -> pd.Series:
#     """
#     Compute daily percentage returns from a validated closing-price Series.
#     """

#     daily_returns = close.pct_change()

#     # If entire Series NaN -> invalid input
#     if daily_returns.isna().all():
#         raise ArithmeticError("Daily returns could not be computed")

#     return daily_returns

def calculate_daily_portfolio_returns(validated_df: pd.DataFrame) -> pd.Series:
    """
    Calculates the daily portfolio total from the input data frame's closing prices and returns their daily percentage change
    
    For simplicity, we'll assume that the user holds a single stock of each company. Variable quantities of particular stock and 
    its calculation will be added later 

    Args: 
    df_test (pandas Dataframe) - storing the name of the stocks as columns and their closing values as row values

    Returns:
    Daily percentage change of the portfolio's total valuation across a time period
    """
    
    df_returns = validated_df.pct_change()

    daily_average_returns = df_returns.dropna().mean(axis=1)

    print(f'daily_average_returns is: {daily_average_returns}')
    return daily_average_returns.pct_change()

def build_price_frame(close_series: pd.Series) -> pd.DataFrame:
    """
    Construct a clean price DataFrame with closing prices and daily_returns columns.
    Index: timestamp
    """
    prices = pd.DataFrame({"close": close_series})
    prices["daily_returns"] = prices["close"].pct_change()

    return prices

# def summarize_returns(raw_df: pd.DataFrame, stock_name: str = "") -> Dict[str, str]:
#     """
#     Summarize performance metrics for a stock based on closing price.

#     Returns:
#         mean_daily_return
#         annualized_volatility
#         total_return
#     """

#     # 1. Validate and extract the closing-price Series
#     close_series = perform_data_validation(raw_df)

#     prices = build_price_frame(close_series)
#     print(prices)

#     daily_returns = prices["daily_returns"].dropna()

#     # 3. Compute metrics
#     total_return = daily_returns.sum()
#     mean_daily_return = daily_returns.mean()
#     annualized_volatility = daily_returns.std() * np.sqrt(252)

#     return {
#         "mean_daily_return": f"{mean_daily_return * 100:.4f}%",
#         "annualized_volatility": f"{annualized_volatility * 100:.4f}%",
#         "total_return": f"{total_return * 100:.4f}%",
#     }


