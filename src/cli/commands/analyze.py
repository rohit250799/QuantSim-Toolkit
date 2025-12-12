from src.modules.analytics.returns_analyzer import (
    #calculate_daily_returns_from_hardcoded_list,
    summarize_returns,
    read_all_csv_data, 
    #calculate_daily_portfolio_returns,
    calculate_daily_returns
)
from typing import List
from pathlib import Path
import pandas as pd
import logging
import argparse

logging.basicConfig(filename='logs/main_file_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

# We can perform analysis on fetch values from the CSV file for analysis. For now, loading
# the CSV file all at once. Later, will create another feature which will use generator to load
# CSV file in chunks if the dataset is large 

def run_analyze(args: argparse.Namespace) -> None:
    logging.debug('Entered the run analyze function block!')
    stock_symbol = args.symbol
    stock_csv_file_path = 'src/data/'
    stock_csv_file_name = f'{stock_symbol}_id.csv'

    file_path = Path(stock_csv_file_path) / stock_csv_file_name
    stock_csv_file_dataframe = read_all_csv_data(stock_symbol)
    logging.debug('The stock symbol is: %s', stock_symbol)

    # if not file_path.is_file():
    #     logging.info('Stock csv file not found in path: %s. Trying analysis from hardcoded list.', stock_csv_file_path)
    #     stock_closing_price_for_testing: List[int] = [100, 102, 101, 105, 107]
    #     stock_closing_price_for_testing_pandas_series: pd.Series = pd.Series(stock_closing_price_for_testing)
    #     result = calculate_daily_returns_from_hardcoded_list(stock_closing_price_for_testing_pandas_series)
    #     print(f'The result is: {result}')
    #     print(summarize_returns(stock_closing_prices_dataframe=stock_closing_price_for_testing_pandas_series, stock_name=stock_symbol))
    #     return
    
    logging.debug('Stock CSV File found in path. Starting the analysis')
    file_data = read_all_csv_data(stock_symbol=stock_symbol)
    result = summarize_returns(stock_csv_file_dataframe)
    print(result)
    return