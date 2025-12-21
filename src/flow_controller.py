from src.data_loader.data_loader import DataLoader
from src.circuit_breaker import CircuitBreaker
from src.data_validator import DataValidator
from src.custom_errors import CircuitOpenStateError
from src.adapters.api_adapter import ApiAdapter

import pandas as pd
import logging
import requests
from datetime import datetime

logging.basicConfig(filename='logs/flow_controller_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

class FlowController:
    def __init__(self, data_loader: DataLoader, circuit_breaker: CircuitBreaker, data_validator: DataValidator) -> None:
        self.data_loader = data_loader
        self.circuit_breaker = circuit_breaker
        self.data_validator = data_validator

    def handle_validation_test(self, ticker: str, mock_file_path: str | None = None):
        """
        Acts as a diagnostic tool - by loading data from a CSV file into pandas dataframe, validates and cleans the data,
        gets validation log to 
        """
        try:
            df = pd.read_csv(f'{mock_file_path}/{ticker}_id.csv')
            logging.info('CSV successfully loaded into dataframe from handle_validation_test function. ')
        except FileNotFoundError:
            logging.debug('File not found in your path. Check your path again!')
            raise
        else:
            clean_and_valid_data = self.data_validator.validate_and_clean(ticker, df)
            validation_logs = self.data_loader.get_validation_log(ticker)

            logging.debug('The dataframe with clean and valid data is: \n%s', clean_and_valid_data)
            logging.debug('The validation logs are: \n%s', validation_logs)

        return 
    
    def dispatch_analysis_request(self, ticker, benchmark, start, end):
        """
        Serves the computation purpose for price data analysis. Fetches price data for both tickers -> if data exists ->
        enters into the analysis module for computation and returns results to the terminal
        """
        
        pass

    def handle_download_request(self, ticker, start_date: str, end_date: str):
        """
        Transforms the user's command into a clean, validated and stored dataset. It is responsible for handling the
        db, network(API) and validator in a single sequence
        """
        self.data_loader.initialize_circuit_state(ticker)
        try:
            circuit_state = self.circuit_breaker.check_circuit_state(ticker)
        except CircuitOpenStateError as e:
            logging.debug('Insode the handle download request function body, circuit open state error has occured')
            logging.info('Since circuit is open, terminating the request and returning. Error: %s', e)
            return
        #except 
        else:
            logging.info('The circuit state from handle download request function is: %s', circuit_state)
            pd_end_date = pd.Timestamp(end_date)
            pd_start_date = pd.Timestamp(start_date)
            logging.info('The end date unix is: %s and the start date unix is: %s', pd_end_date, pd_start_date)
            
            api_adapter = ApiAdapter()
            try:
                api_call_data = api_adapter.fetch_data(ticker, pd_start_date, pd_end_date)
                logging.debug('The api call returned data in handle download request is: \n%s', api_call_data)
            except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, TimeoutError, requests.exceptions.HTTPError) as e:
                logging.debug('Inside the handle download request function, the api call has failed. Error: %s', e)
                self.circuit_breaker.handle_failure(ticker)
                return
            else:
                clean_data = self.data_validator.validate_and_clean(ticker, df=api_call_data)
                logging.debug('The data as param in validate and clean, as dataframe is: \n%s', api_call_data)
                self.data_loader.insert_daily_data(ticker=ticker, df=clean_data)
        return

