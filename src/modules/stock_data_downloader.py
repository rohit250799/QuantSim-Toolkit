import logging
from pathlib import Path
import os
import requests
import pandas as pd
import asyncio
import time

from dotenv import load_dotenv

logging.basicConfig(filename='QuantSim-Toolkit/logs/my_log_file.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

load_dotenv()

class FinancialDataDownloader:
    def __init__(self):
        self.api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', 'key not found')
        self.base_url: str = 'https://www.alphavantage.co'

    def download_historical_stock_data(self, stock_symbol: str, market: str = 'BSE', timeframe='id', save_path='data/') -> str:
        """
        Download stock data in CSV format    
        """
        url = f'{self.base_url}/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}.{market}&apikey={self.api_key}&datatype=csv'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response: requests.Response = requests.get(url=url, headers=headers, timeout=2.50)
        response.raise_for_status()

        Path(save_path).mkdir(exist_ok=True)

        filename = f'{save_path}{stock_symbol}_{timeframe}.csv'

        #saving raw CSV
        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f'Stock data for symbol: {stock_symbol} saved in file: {filename}')
        return filename
    
    def fetch_daily_data(self, symbol: str, market: str = 'BSE') -> dict:
        """
        Get the raw daily time series of the global equity, covering 20+ years of historical data
        """
        url: str = f'{self.base_url}/query?function=TIME_SERIES_DAILY&symbol={symbol}.{market}&outputsize=compact&apikey={self.api_key}'
        headers = {'Authorization': f'Bearer {self.api_key}'}

        try:
            response: requests.Response = requests.get(url=url, headers=headers, timeout=10)
            response_code = response.status_code

            if response_code == 200:
                print('Reqeust has been successful') 
                return response.json()

            elif response_code == 429:
                wait_time = 60
                print(f'429 Error: Too many requests. Retry after {wait_time} seconds...')
                time.sleep(wait_time)
                return self.fetch_daily_data(symbol, market)    

            elif response_code >= 500 and response_code < 600:
                wait_time = 30
                print(f'Server error {response_code}: Wait for 30 seconds before retrying')
                time.sleep(wait_time)
                return self.fetch_daily_data(symbol, market)

            else: 
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Reques failed: {e}')
            raise ConnectionError         
    
    def load_as_dataframe(self, csv_path):
        """Load the downloaded CSV data as Pandas dataframe"""
        if not csv_path:
            raise FileNotFoundError('The file could not be found')
        with open(csv_path, 'r', encoding='utf-8') as file:
            # pd.read_csv(csv_path)
            for chunk in pd.read_csv(file, chunksize=1000):
                yield chunk
                

result_class = FinancialDataDownloader()

data = result_class.fetch_daily_data(symbol='INFY', market='BSE')
print(data)