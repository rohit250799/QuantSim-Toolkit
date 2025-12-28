"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""
import logging
from collections.abc import Generator
from typing import Any, Dict, Tuple

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

def calculate_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the log returns of closing prices from the dataframe
    """
    price_columns = ['ticker_close', 'benchmark_close']
    return_cols = [col + '_log_return' for col in price_columns]
    df[return_cols] = np.log(df[price_columns] / df[price_columns].shift(1))
    #logger.info('The updated dataframe with log returns is: \n%s', df)
    return (df[return_cols])

def calculate_cummulative_returns(df: pd.DataFrame) -> Tuple[np.float64, np.float64]:
    """
    Calculates and returns the commulative returns of the stock over the entire period
    """
    ticker_initial_price = df['ticker_close'].iloc[0]
    ticker_final_price = df['ticker_close'].iloc[-1]

    benchmark_initial_point = df['benchmark_close'].iloc[0]
    benchmark_final_point = df['benchmark_close'].iloc[-1]

    ticker_cummulative_return = (ticker_final_price / ticker_initial_price - 1)
    benchmark_cummulative_return = (benchmark_final_point / benchmark_initial_point - 1)

    logger.info('The ticker cummulative return is: %s and the benchmark cummulative return is: %s', ticker_cummulative_return, benchmark_cummulative_return)
    return (ticker_cummulative_return, benchmark_cummulative_return)

def calculate_annualized_volatility(df: pd.DataFrame) -> Tuple[np.float64, np.float64]:
    """
    Calculates the Standard Deviation of the ticker's daily returns and returns its annualized value
    """
    ticker_daily_returns_standard_deviation = df['ticker_close_log_return'].std(skipna=True)
    benchmark_daily_returns_standard_deviation = df['benchmark_close_log_return'].std(skipna=True)

    ticker_annualized_volatility = ticker_daily_returns_standard_deviation * (252 ** 0.5)
    benchmark_annualized_volatility = benchmark_daily_returns_standard_deviation * (252 ** 0.5)

    logger.info('The ticker annualized volatility: %s', ticker_annualized_volatility)
    logger.info('The benchmark annualized volatility: %s', benchmark_annualized_volatility)
    return (ticker_annualized_volatility, benchmark_annualized_volatility)

def calculate_covariance(df: pd.DataFrame) -> float:
    """
    Calculates the sample covariance between the ticker and benchmark from the given dataframe    
    """
    df = df.dropna()
    ticker_log_returns_series = df['ticker_close_log_return'].to_numpy(dtype=float)
    benchmark_log_returns_series = df['benchmark_close_log_return'].to_numpy(dtype=float)
    covariance: float = float(np.cov(ticker_log_returns_series, benchmark_log_returns_series, ddof=1)[0, 1])
    #covariance: float = df['ticker_close_log_return'].cov(df['benchmark_close_log_return'])
    logger.info('The sample covariance is: %s', covariance)
    return covariance

def calculate_beta(df: pd.DataFrame) -> float:
    """
    Calculates the market sensitivity (Beta value). It implies how much the stock moves for every 1% move in the market

    Things to keep in mind:
    Statistical significance - Need at least 30 to 60 days 
    Checking for stationarity - Returns should not have trends
    For time-varying sensitivity - Consider using rolling-beta (a 60 day window)
    Beta is the regression slope - ticker_return = alpha + beta * benchmark_return + error
    """
    df = df.dropna()
    covariance_between_ticker_and_benchmark: float = calculate_covariance(df)
    ticker_log_returns_series = df['ticker_close_log_return'].to_numpy(dtype=float)
    benchmark_log_returns_series = df['benchmark_close_log_return'].to_numpy(dtype=float)
    sample_variance_of_benchmark_log_returns: float = float(benchmark_log_returns_series.var(ddof=1))

    if sample_variance_of_benchmark_log_returns == 0:
        raise ZeroDivisionError('Benchmark variance is 0. Please calculate again!')

    beta_value = covariance_between_ticker_and_benchmark / sample_variance_of_benchmark_log_returns
    logger.info('The beta value is: %s', beta_value)

    return beta_value

def calculate_log_return_alpha(df: pd.DataFrame) -> float:
    """
    Calculates the Alpha (Log Returns alpha). It implies the excess log performance of a stock, adjusted against its risk.

    Interpretations:
    Positive alpha - stock outperformed its risk-adjusted expectation
    Negative alpha - stock underperformed
    Zero alpha - stock performed exactly as CAPM predicted

    Things to keep in mind:
    Statistical significance - Need many periods (at least > 60 days)
    Alpha can be misleading if the Beta or annualized risk-free rate are wrong (using a default 5% rate here)
    To compare against a common benchmark - Use a 3-month treasury bill for risk-free calculation
    Jensen's Alpha is the intercept in the CAPM regression 
    """
    average_ticker_daily_log_return = df['ticker_close_log_return'].mean()
    average_benchmark_daily_log_return = df['benchmark_close_log_return'].mean()

    beta = calculate_beta(df)
    annualized_risk_free_rate = 0.05
    daily_risk_free_rate = (1 + annualized_risk_free_rate) ** (1/252) - 1

    logger.info('The Daily risk free rate: %s', daily_risk_free_rate)

    # expected_return = daily_risk_free_rate + beta * (average_benchmark_daily_log_return - daily_risk_free_rate)

    # jensen_alpha = average_ticker_daily_log_return - beta * average_benchmark_daily_log_return
    # annualized_jensen_alpha = jensen_alpha * 252
    # logger.info('The Jensen\'s Alpha is: %s and annualized jensen alpha is: %s', jensen_alpha, annualized_jensen_alpha)
    log_alpha_daily = average_ticker_daily_log_return - beta * average_benchmark_daily_log_return
    annualized_log_alpha = log_alpha_daily * 252
    logger.info('The annualized log alpha is: %s', annualized_log_alpha)
    return annualized_log_alpha

def calculate_sharp_ratio(df: pd.DataFrame) -> float:
    """
    Calculates the Sharpe Ratio (or Risk Adjusted Return) of a ticker against a benchmark. It helps the user in understanding if 
    the returns are due to smart investing or just taking excessive risk

    Returns -  the Annualized Sharpe Ratio
    """
    average_ticker_daily_log_return: float = df['ticker_close_log_return'].mean()
    annualized_risk_free_rate: float = 0.05
    daily_risk_free_rate: float = (1 + annualized_risk_free_rate) ** (1/252) - 1

    excess_return = average_ticker_daily_log_return - daily_risk_free_rate
    daily_volatility: float = df['ticker_close_log_return'].std()
    daily_sharpe_ratio = excess_return / daily_volatility
    annualized_sharpe_ratio: float = daily_sharpe_ratio * (252 ** 0.5)

    logger.info('The daily sharpe ratio is: %s and the annualized sharpe ratio is: %s', daily_sharpe_ratio, annualized_sharpe_ratio)   
    return annualized_sharpe_ratio

def calculate_correlation_coefficient(df: pd.DataFrame) -> float:
    """
    Calculates the statistical Pearson correlation between the ticker and the benchmark. Implies how to Financial entities
    move together

    Interpretation:
    If correlation == +1 : Implies perfect positive correlation (move exactly together)
    If correlation == 0 : Implies no relationship
    If correlation == -1: Implies perfect negative correlation (moves exactly opposite)
    If correlation between 0.7 and 0.9 approx - Implies typical stock vs market correlation
    If correlation == Negative : Implies a hedging potential

    Key notes:
    Stationarity requirement - Uses returns, not prices
    Needs sufficient data -  > 30 days for reliability
    Correlation != Causation
    It can help in calculating rolling correlation for time-varying relationship
    """

    correlation = df['ticker_close_log_return'].corr(df['benchmark_close_log_return'])
    logger.info('The correlation is: %s', correlation)

    return correlation
    
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
