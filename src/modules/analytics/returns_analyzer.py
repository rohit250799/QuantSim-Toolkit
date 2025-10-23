"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""

import pandas as pd

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

for series_chunk in read_csv_stock_data_in_chunks("TCS"):
    print(series_chunk)
    print("-" * 40)

# def calculate_daily_returns():
#     pass
