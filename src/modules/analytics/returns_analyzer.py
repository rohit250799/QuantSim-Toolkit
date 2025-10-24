"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""

import pandas as pd
import logging

logging.basicConfig(filename='my_log_file.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

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

def calculate_daily_returns(stock_closing_prices_series: pd.Series):
    """
    Calculates the daily arithmetic returns of a stock and returns it as a Pandas series
    """
    if not stock_closing_prices_series:
        raise ValueError('The series is empty!')
    
    if len(stock_closing_prices_series) < 2:
        raise ValueError('Calculations are not possible with a single value')
    
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

stock_name = input('Enter the stock name: ')

for daily_returns_series_chunk in calculate_daily_returns(stock_closing_prices_series=stock_name):
    print(daily_returns_series_chunk)
    print('_____')


