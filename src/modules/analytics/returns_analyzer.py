"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""
import logging
from collections.abc import Generator
from typing import Any, Dict, cast

import pandas as pd
import numpy as np

logging.basicConfig(filename='logs/main_file_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

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
    
def perform_data_validation(df: pd.DataFrame) -> pd.Series:
    """
    All data validation is performed here and then the clean data is used for all the calculations and analysis
    """

    if "close" not in df.columns:
        raise KeyError("Input DataFrame must contain a 'close' column")

    cleaned = df.loc[
        (df["close"] > 0)
        & (df["close"].notna())
        & (np.isfinite(df["close"]))
    , "close"]

    if cleaned.empty:
        raise ArithmeticError("No valid closing prices available after filtering")

    # Ensuring Series returned (not DataFrame)
    cleaned = cleaned.astype(float)

    return cast(pd.Series, cleaned)

    

# def calculate_daily_returns(stock_closing_prices_dataframe: pd.DataFrame, stock_name = None):
#     """
#     Calculates the daily arithmetic returns of a stock and returns it as a Pandas series

#     args:
#     stock_closing_price_series(pandas Series) - a numberical series in Pandas which has the date as index and
#     everyday closing prices of the stock as values

#     returns:
#     a Pandas numerical series which returns the daily percentage change of a stock from its closing price in
#     format- date: percentage_change

#     """   
#     #my_generator = read_csv_stock_data_in_chunks(stock_name)
#     #file_data = read_all_csv_data(stock_name)
#     #prev_last_price = None  # store last price of previous chunk

#     # for chunk in my_generator:
#     #     returns = chunk.pct_change()

#     #     # If previous chunk exists, compute return for first element
#     #     if prev_last_price is not None:
#     #         first_return = (chunk.iloc[0] - prev_last_price) / prev_last_price
#     #         returns.iloc[0] = first_return

#     #     # Drop NaN for clean output (optional)
#     #     yield returns.dropna()

#     #      # Update previous last price
#     #     prev_last_price = chunk.iloc[-1]
#     #stock_closing_prices_dataframe['daily return'] = stock_closing_prices_dataframe['close'].pct_change()
#     #print(f'stock_closing_prices_dataframe is: {stock_closing_prices_dataframe}')
#     return stock_closing_prices_dataframe.pct_change()


def calculate_daily_returns(close: pd.Series) -> pd.Series:
    """
    Compute daily percentage returns from a validated closing-price Series.
    """

    daily_returns = close.pct_change()

    # If entire Series NaN -> invalid input
    if daily_returns.isna().all():
        raise ArithmeticError("Daily returns could not be computed")

    return daily_returns


# def calculate_daily_returns_from_hardcoded_list(stock_closing_price_for_testing_pandas_series: pd.Series) -> pd.Series[float]:
#     """
#     Accepts a pandas series of values and returns their daily percentage change

#     Args:
#     stock_closing_price_for_testing_pandas_series(pandas Series) - Closing prices of a stock 

#     Returns: 
#     The daily percentage change of the stock
#     """
#     if stock_closing_price_for_testing_pandas_series.empty:
#         raise ValueError('The pandas series is empty!')
    
#     if stock_closing_price_for_testing_pandas_series.size < 2:
#         raise ValueError('Calculations not possible with single value')
    
#     return stock_closing_price_for_testing_pandas_series.pct_change()

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

# def summarize_returns(stock_closing_prices_dataframe: pd.Series | None, stock_name: str = '') -> Dict[str, int]:
#     """
#     Summarizes the returns of a particular stock and returns the key performance indicators to the user

#     Args:
#     stock_closing_prices_series(pandas series) - a Pandas series with date_timestamp as the index and closing prices as values

#     Returns:
#     A dictionary containing values of total returns, annualized volatility and mean daily return
#     """
#     csv_dataframe = read_all_csv_data(stock_name)            
#     clean_data = perform_data_validation(csv_dataframe)
#     close = csv_dataframe['close']
    
#     clean_data['daily_returns'] = calculate_daily_returns(close, stock_name)
#     daily_returns = clean_data['daily_returns'].dropna()

#     total_returns = daily_returns.sum()
#     mean_daily_return = daily_returns.mean()
#     annualized_volatility = daily_returns.std() * (252 ** 0.5)

#     return {
#         "mean_daily_return": mean_daily_return,
#         "annualized_volatility": annualized_volatility,
#         "total_return": total_returns
#     }

def build_price_frame(close_series: pd.Series) -> pd.DataFrame:
    """
    Construct a clean price DataFrame with closing prices and daily_returns columns.
    Index: timestamp
    """
    prices = pd.DataFrame({"close": close_series})
    prices["daily_returns"] = prices["close"].pct_change()

    return prices

def summarize_returns(raw_df: pd.DataFrame, stock_name: str = "") -> Dict[str, str]:
    """
    Summarize performance metrics for a stock based on closing price.

    Returns:
        mean_daily_return
        annualized_volatility
        total_return
    """

    # 1. Validate and extract the closing-price Series
    close_series = perform_data_validation(raw_df)

    prices = build_price_frame(close_series)
    print(prices)

    daily_returns = prices["daily_returns"].dropna()

    # 3. Compute metrics
    total_return = daily_returns.sum()
    mean_daily_return = daily_returns.mean()
    annualized_volatility = daily_returns.std() * np.sqrt(252)

    return {
        "mean_daily_return": f"{mean_daily_return * 100:.4f}%",
        "annualized_volatility": f"{annualized_volatility * 100:.4f}%",
        "total_return": f"{total_return * 100:.4f}%",
    }


