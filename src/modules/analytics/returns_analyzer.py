"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""
import logging

import pandas as pd

logging.basicConfig(filename='QuantSim-Toolkit/logs/my_log_file.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

stock_name = input('Enter the stock name: ')


def read_csv_stock_data_in_chunks(stock_symbol: str, chunksize: int = 10):
    """
    A generator to read stock data from the csv file in chunks and reorganises that in Series format with timestamp as index

    Args:
    stock_symbol: str - Symbol of the stock, since csv files are saved starting with their symbol name
    chunksize: int - size of the chunk in which the data is to be broken

    Returns:
    Pandas series with the timestamp values as the index and closing price of the stock as values
    """
    try:
        file_path: str = f'QuantSim-Toolkit/src/data/{stock_symbol}_id.csv'
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

def read_all_csv_data(stock_symbol: str):
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
        file_path: str = f'QuantSim-Toolkit/src/data/{stock_symbol}_id.csv'
    except FileNotFoundError:
        print('Invalid path! File not found there')
    else:
        df = pd.read_csv(file_path, usecols=['timestamp', 'close'], parse_dates=['timestamp'], index_col=['timestamp'])
        df = df.sort_values('timestamp')

        return df

    

def calculate_daily_returns(stock_closing_prices_series: pd.Series):
    """
    Calculates the daily arithmetic returns of a stock and returns it as a Pandas series

    args:
    stock_closing_price_series(pandas Series) - a numberical series in Pandas which has the date as index and
    everyday closing prices of the stock as values

    returns:
    a Pandas numerical series which returns the daily percentage change of a stock from its closing price in
    format- date: percentage_change

    """
    # if not stock_closing_prices_series:
    #     raise FileNotFoundError('There is no file with that name!')

    # if stock_closing_prices_series.empty: 
    #     raise ValueError('The series is empty!')
    
    # if len(stock_closing_prices_series) < 2:
    #     raise ValueError('Calculations are not possible with a single value')
    
    my_generator = read_csv_stock_data_in_chunks(stock_name)

    prev_last_price = None  # store last price of previous chunk

    for chunk in my_generator:
        returns = chunk.pct_change()

        # If previous chunk exists, compute return for first element
        if prev_last_price is not None:
            first_return = (chunk.iloc[0] - prev_last_price) / prev_last_price
            returns.iloc[0] = first_return

        # Drop NaN for clean output (optional)
        yield returns.dropna()

         # Update previous last price
        prev_last_price = chunk.iloc[-1]

def calculate_daily_returns_from_hardcoded_list(stock_closing_price_for_testing_pandas_series: pd.Series):
    """
    Accepts a pandas series of values and returns their daily percentage change

    Args:
    stock_closing_price_for_testing_pandas_series(pandas Series) - Closing prices of a stock 

    Returns: 
    The daily percentage change of the stock
    """
    if stock_closing_price_for_testing_pandas_series.empty:
        raise ValueError('The pandas series is empty!')
    
    if stock_closing_price_for_testing_pandas_series.size < 2:
        raise ValueError('Calculations not possible with single value')
    
    return stock_closing_price_for_testing_pandas_series.pct_change()

def calculate_daily_portfolio_returns(df_test: pd.DataFrame) -> pd.Series:
    """
    Calculates the daily portfolio total from the input data frame's closing prices and returns their daily percentage change
    
    For simplicity, we'll assume that the user holds a single stock of each company. Variable quantities of particular stock and 
    its calculation will be added later 

    Args: 
    df_test (pandas Dataframe) - storing the name of the stocks as columns and their closing values as row values

    Returns:
    Daily percentage change of the portfolio's total valuation across a time period
    """
    
    df_returns = df_test.pct_change()

    daily_average_returns = df_returns.mean(axis=1)

    print(f'daily_average_returns is: {daily_average_returns}')
    return daily_average_returns.pct_change()

def summarize_returns(stock_closing_prices_series: pd.Series = read_all_csv_data(stock_symbol=stock_name)) -> dict:
    """
    Summarizes the returns of a particular stock and returns the key performance indicators to the user

    Args:
    stock_closing_prices_series(pandas series) - a Pandas series with date_timestamp as the index and closing prices as values

    Returns:
    A dictionary containing values of total returns, annualized volatility and mean daily return
    """

    returns_output_dict: dict['str': float] = {}

    daily_returns_from_stock_price = calculate_daily_returns_from_hardcoded_list(stock_closing_prices_series).round(decimals=4)
    total_returns: float = daily_returns_from_stock_price.sum()
    num_of_values_in_series: int = daily_returns_from_stock_price.size - 1
    mean_daily_return = total_returns / num_of_values_in_series
    returns_output_dict['mean_daily_return'] = mean_daily_return
    daily_standard_deviation_in_stock_closing_prices = daily_returns_from_stock_price.std()
    annualized_volatility: float = daily_standard_deviation_in_stock_closing_prices * (252 ** 0.5)
    returns_output_dict['annualized_volatility'] = annualized_volatility
    returns_output_dict['total_return'] = total_returns

    return returns_output_dict




user_choice_for_testing = int(input('Enter 1 to test with CSV file values and 2 for testing with hardcoded ' \
'price values and 3 for testing portfolio sum daily: '))

df_test = pd.DataFrame({
    'TCS': [100.0, 102.0, 101.0, 105.0, 104.0],
    'INFY': [200.0, 198.0, 202.0, 205.0, 208.0],
    'RELIANCE': [150.0, 152.0, 149.0, 155.0, 158.0]
}, index=pd.date_range(start='2024-01-01', periods=5, freq='D'))


if user_choice_for_testing == 1:
    stock_name = input('Enter the stock name: ')
    for daily_returns_series_chunk in calculate_daily_returns(stock_closing_prices_series=stock_name):
        print(daily_returns_series_chunk)
    print('_____')
    print(summarize_returns())

elif user_choice_for_testing == 2:
    stock_closing_price_for_testing: list = [100, 102, 101, 105, 107]
    stock_closing_price_for_testing_pandas_series: pd.Series = pd.Series(stock_closing_price_for_testing)
    result = calculate_daily_returns_from_hardcoded_list(stock_closing_price_for_testing_pandas_series)
    print(f'The result is: {result}')
    print(summarize_returns(stock_closing_prices_series=stock_closing_price_for_testing_pandas_series))

elif user_choice_for_testing == 3:
    result = calculate_daily_portfolio_returns(df_test)
    print(result)


else: 
    print('Invalid choice')
    raise KeyError('Choose between 1 and 2!')



