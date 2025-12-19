from src.data_loader.data_loader import DataLoader
from src.circuit_breaker import CircuitBreaker
from src.data_validator import DataValidator

import pandas as pd
import logging

logging.basicConfig(filename='logs/flow_controller_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

class FlowController:
    def __init__(self, data_loader: DataLoader, circuit_breaker: CircuitBreaker, data_validator: DataValidator) -> None:
        self.data_loader = data_loader
        self.circuit_breaker = circuit_breaker
        self.data_validator = data_validator

    def handle_validation_test(self, ticker: str, mock_file_path: str):
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
    
    def dispatch_analysis_request(self, config):
        """
        Calls handle_download_request for the benchmark ticker first, then for the target ticker. Once data is ready, calls

        """
        self.handle_download_request()
        pass

    def handle_download_request(self, ticker, start_date):
        """
        Transforms the user's command into a clean, validated and stored dataset. It is responsible for handling the
        db, network(API) and validator in a single sequence
        """

        pass

