from src.modules.analytics.returns_analyzer import (
    calculate_daily_returns_from_hardcoded_list,
    summarize_returns,
    read_all_csv_data, calculate_daily_portfolio_returns
)
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(filename='logs/main_file_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

# We can perform analysis on hardcoded list values or fetch values from the CSV file for analysis. For now, focusing
# on hardcoded list

def run_analyze(args):
    logging.debug('Entered the run analyze function block!')
    stock_symbol = args.symbol
    stock_csv_file_path = 'src/data/'
    stock_csv_file_name = f'{stock_symbol}_id.csv'

    file_path = Path(stock_csv_file_path) / stock_csv_file_name

    logging.debug('The stock symbol is: %s', stock_symbol)

    if not file_path.is_file():
        logging.info('Stock csv file not found in path: %s. Trying analysis from hardcoded list.', stock_csv_file_path)
        stock_closing_price_for_testing: list = [100, 102, 101, 105, 107]
        stock_closing_price_for_testing_pandas_series: pd.Series = pd.Series(stock_closing_price_for_testing)
        result = calculate_daily_returns_from_hardcoded_list(stock_closing_price_for_testing_pandas_series)
        print(f'The result is: {result}')
        print(summarize_returns(stock_closing_prices_series=stock_closing_price_for_testing_pandas_series, stock_name=stock_symbol))
        return
    
    #print("CSV file found")
    logging.debug('Stock CSV File found in path. Starting the analysis')
    file_data = read_all_csv_data(stock_symbol=stock_symbol)
    daily_portfolio_returns = calculate_daily_portfolio_returns(file_data)
    print(summarize_returns(daily_portfolio_returns, stock_symbol))
    return