import pandas as pd
import logging
import os
import time
import requests
from typing import Dict, cast, Any

logging.basicConfig(
    filename='logs/api_response_logs.txt', level=logging.DEBUG,
    format=' %(asctime)s -  %(levelname)s -  %(message)s'
)

class ApiAdapter:
    """
    Ensures that the rest of the system never sees a JSON string or raw API dict.
    Acts as the format firewall
    """

    def __init__(self) -> None:
        self.api_key: str = os.environ.get('ALPHA_VANTAGE_API_KEY', 'key not found')
        self.base_url: str = 'https://www.alphavantage.co'

    def _api_call_with_retry(self, symbol: str, params: dict | None):
        """
        Returns: a dict containing the raw JSON response on success or None if the exhaustion point is reached without a successful
        response from the API call
        """
        url: str = f'{self.base_url}/query?function=TIME_SERIES_DAILY&symbol={symbol}.BSE&outputsize=5&apikey={self.api_key}'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        fetching_failure_counts = 0
        max_retries_allowed = 5
        current_trial_number = 0

        while current_trial_number < max_retries_allowed:
            wait_time = (2 ^ current_trial_number)
            api_calling_response = requests.get(url=url, headers=headers, timeout=(5, 20))
            api_calling_response_code = api_calling_response.status_code

            if api_calling_response_code == 200:
                if "Error Message" in api_calling_response.text:
                    logging.debug('The error is: %s', api_calling_response.text)
                    logging.debug('Error in API response. Please check your parameters again')
                    return 
                elif "Note" in api_calling_response.text:
                    logging.debug('The error is: %s', api_calling_response.text)                
                    logging.info('Soft rate limit')
                    fetching_failure_counts += 1
                    time.sleep(wait_time)
                    current_trial_number += 1
                elif "Time Series (Daily)" in api_calling_response.text:
                    logging.info('API call successful from api call with retry function')
                    raw_data = api_calling_response.json()
                    logging.debug('The raw data from the api call is: %s', raw_data)
                    response_dict_data = cast(Dict[str, Any], raw_data)
                    logging.debug('The response dict data is: %s', response_dict_data)
                    return response_dict_data
                else:
                    logging.debug('Unknown or Empty response. Implementing exponential backoff strategy by sleeping for %d seconds', wait_time)
                    current_trial_number += 1
                    time.sleep(wait_time)
                    fetching_failure_counts += 1
            else:
                logging.debug('Some http errors have occured. Implementing backoff by sleeping for %d seconds', wait_time)
                fetching_failure_counts += 1
                time.sleep(wait_time)
                current_trial_number += 1
        logging.debug('5 attempts have been used. Returning None')
        return

    def fetch_data(self, ticker: str, start_date: pd.Timestamp, end_date: pd.Timestamp):
        """
        Acts as the sanitizer in the system. It calls the _api_call_with_retry function (procurement logic) and if proper data is returned from the 
        API response in a Dict format, it converts the dict into a pandas DataFrame with the timestamp as dateindex.

        No data insertion is done here

        Returns: A filtered Pandas dataframe from start to end date parameters ig valid data was returned from the api call or else, None
        """
        api_call_with_retry_result = self._api_call_with_retry(symbol=ticker, params=None)
        if not api_call_with_retry_result:
            logging.info('In fetch data function, the api call with retry returned Falsy values. So, we return None')
            return
        logging.debug('The api call with retry result in fetch data is: %s', api_call_with_retry_result)
        ts = api_call_with_retry_result.get('Time Series (Daily)')
        if not ts:
            logging.info('No key Time Series (Daily). Raising Key error')
            raise KeyError('Key not found')
        
        df = (
        pd.DataFrame.from_dict(ts, orient="index").rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
          }))

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        df = df.astype({
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "int64"
        })

        filtered_dataframe_based_on_daterange = df.loc[start_date:end_date]
        logging.debug('The filtered dataframe is: %s', filtered_dataframe_based_on_daterange)
        return filtered_dataframe_based_on_daterange