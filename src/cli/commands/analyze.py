from src.modules.analytics.returns_analyzer import (
    summarize_returns,
    read_all_csv_data, 
    #calculate_daily_portfolio_returns,
    calculate_daily_returns
)
from src.flow_controller import FlowController

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

def run_analyze(args: argparse.Namespace, flow_controller: FlowController | None) -> None:
    logging.debug('Entered the run analyze function block!')
    stock_symbol = args.symbol
    stock_csv_file_path = 'src/data/'
    stock_csv_file_name = f'{stock_symbol}_id.csv'

    file_path = Path(stock_csv_file_path) / stock_csv_file_name
    stock_csv_file_dataframe = read_all_csv_data(stock_symbol)
    logging.debug('The stock symbol is: %s', stock_symbol)
    
    logging.debug('Stock CSV File found in path. Starting the analysis')
    file_data = read_all_csv_data(stock_symbol=stock_symbol)
    result = summarize_returns(stock_csv_file_dataframe)
    print(result)
    return