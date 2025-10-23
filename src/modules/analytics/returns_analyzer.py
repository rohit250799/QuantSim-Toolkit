"""
This file is responsible for analysing the stock value and calculating the daily returns from it
"""

import pandas as pd

# time_index_start_date = ''
# time_index_end_date = ''

date_range_index = pd.date_range(start='2025-05-29', periods=30)

def find_closing_prices_of_stocks_from_csv(stock_symbol: str):
    try: 
        file_path: str = f'QuantSim-Toolkit/src/data/{stock_symbol}_id.csv'
    except FileNotFoundError:
        print('Invalid path! File not found there')
    else: 
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            for row in csv_file:
                yield row.split(',')[4]

stock_closing_prices = find_closing_prices_of_stocks_from_csv('TCS')
column_headings = next(stock_closing_prices)

while True:
    print(next(stock_closing_prices))

# def calculate_daily_returns():
#     pass