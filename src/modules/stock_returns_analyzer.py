import logging
import requests
import os
import pandas as pd

from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(filename='my_log_file.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

load_dotenv()

class FinancialDataDownloader:
    def __init__(self):
        self.api_key = os.environ.get('API_KEY', 'key not found')
        self.base_url = 'https://www.alphavantage.co'

    def download_historical_stock_data(self, stock_symbol: str, timeframe='id', save_path='data/'):
        """
        Download stock data in CSV format    
        """
        url = f'{self.base_url}/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=5min&apikey={self.api_key}&datatype=csv'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(url=url, headers=headers, timeout=2.50)
        response.raise_for_status()

        Path(save_path).mkdir(exist_ok=True)

        filename = f'{save_path}{stock_symbol}_{timeframe}.csv'

        #saving raw CSV
        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f'Stock data for symbol: {stock_symbol} saved in file: {filename}')
        return filename
    
    def load_as_dataframe(self, csv_path):
        """Load the downloaded CSV data as Pandas dataframe"""
        return pd.read_csv(csv_path)

downloader = FinancialDataDownloader()
csv_file = downloader.download_historical_stock_data("AAPL", "1d")
df = downloader.load_as_dataframe(csv_file)

print(df.head())