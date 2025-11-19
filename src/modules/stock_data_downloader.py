from pathlib import Path
import os
import logging
import time
from datetime import datetime, timedelta
import requests
import pandas as pd

from src.custom_errors import RecordNotFoundError



from dotenv import load_dotenv
from enum import Enum
from db.database import execute_query, insert_bulk_data, DB_PATH

logging.basicConfig(filename='logs/api_response_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

load_dotenv()

class Circuit_State(Enum):
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2

class Error_Type(Enum):
    API_RATE_LIMIT = 0
    API_SERVER_ERROR = 1
    NETWORK_TIMEOUT = 2
    VALIDATION_ERROR = 3
    CIRCUIT_OPEN = 4
    UNEXPECTED_ERROR = 5

class Resolution(Enum):
    RETRIED = 0
    SKIPPED = 1
    ABORTED = 2
    CONTINUED = 3

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
    
    def _check_circuit_state(self, symbol: str) -> bool:
        """
        Checks the current state of the circuit breaker

        Args:
        symbol(str) - stock symbol for which we are checking the state

        Returns:
        A tuple denoting the permisson for API calls(bool) and current state(int) - if True is returned, API calls will be allowed for the stock. Else, 
        API calls have been suspended for a time period and will resume later

        Raises:
        RecordNotFoundError if the symbol does not exist in the database
        """
        get_symbol_id: tuple = execute_query(DB_PATH, "select id from symbols where ticker = ?", (symbol, ))
        symbol_id: int = int(get_symbol_id[0]) if get_symbol_id else 0
        if symbol_id:
            record_existence_in_circuit_breaker_states_table = execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, ))
            if not record_existence_in_circuit_breaker_states_table:
                init_state = Circuit_State.CLOSED.value
                init_failure_count = 0
                init_last_failure_time = None
                init_cooldown_end_time = None
                execute_query(DB_PATH, "insert into circuit_breaker_states(symbol_id, failure_count, last_fail_time, state, cooldown_end_time) values(?, ?, ?, ?, ?)", (symbol_id, init_failure_count, init_last_failure_time, init_state, init_cooldown_end_time))
                logging.debug("After inserting record in table, the record is: %s", execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))
            else:
                current_symbol_state, cooldown_end_time = execute_query(DB_PATH, "select state, cooldown_end_time from circuit_breaker_states where symbol_id = ?", (symbol_id, ))
                logging.debug('The symbol state is: %s and cooldown end time is: %s', current_symbol_state, cooldown_end_time)
                
        else: 
            raise RecordNotFoundError('The symbol id has not been found in the database. Check your symbol id again')
        
        if current_symbol_state == 0:
            return True, current_symbol_state
        elif current_symbol_state == 1:
            current_timestamp: datetime = datetime.now()
            cooldown_end_time: str = execute_query(DB_PATH, "select cooldown_end_time from circuit_breaker_states where symbol_id = ?", (symbol_id, ))[0]
            cooldown_end_time_datetime: datetime = datetime.fromisoformat(cooldown_end_time) if cooldown_end_time else datetime.min

            if current_timestamp > cooldown_end_time_datetime:
                updated_state = Circuit_State.HALF_OPEN.value
                updated_failure_count = 0
                updated_last_failure_time = None
                updated_cooldonw_end_time = None
                execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ?, cooldown_end_time = ? where symbol_id = ?", (updated_failure_count, updated_last_failure_time, updated_state, updated_cooldonw_end_time, symbol_id))
                logging.debug("Since current time > cooldown_end time, updating record. New record = %s", execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))

                return True, updated_state
            else: 
                return False, current_symbol_state
        else: 
            return True, current_symbol_state
    
    def fetch_daily_data(self, symbol: str, market: str = 'BSE') -> dict:
        """
        Get the raw daily time series of the global equity, covering 20+ years of historical data. It acts as the Business Logic orchestrator.

        Args:
        symbol(str) - The symbol (Ticker) of the stock that we are interested in fetching data of
        marker(str) - The market where that particular stock is listed and from which, the data will get fetched

        Returns:
        Processed data from API call success (dict) or an empty dict in case of failure
        """
    
        #fetching_failure_counts: int = 0
        current_timestamp_in_iso_format = datetime.now().isoformat()

        circuit_state_func_result, current_symbol_state = self._check_circuit_state(symbol=symbol)
        if circuit_state_func_result:
            api_calling: bool = self._api_call_with_retry(symbol=symbol, market=market)
            if api_calling:
                self._update_circuit_state(symbol=symbol, success=True)
                return api_calling
            else:
                self._update_circuit_state(symbol=symbol, success=False)

                return {}
        else: #in case the circuit state is Open
            logging.debug('The circuit state is Open now. So, skipping the call.')
            execute_query(DB_PATH, "insert into error_metrics(timestamp, error_type, resolution) values(?, ?, ?)", (current_timestamp_in_iso_format, Error_Type.CIRCUIT_OPEN.value, Resolution.SKIPPED.value))
            logging.debug('After inserting values for open circuit, the record is: %s', execute_query(DB_PATH, "select * from error_metrics where timestamp = ?", (current_timestamp_in_iso_format, )))
            return {}
            

    def _update_circuit_state(self, symbol: str, success: bool) -> None:
        """
        Updates the circuit state and stores it in the db

        Args:
        symbol(str) - stock symbol(ticker) used to identify the stock
        success(bool) - API call result (returns True if API call succeeded and False if it failed)

        Returns:
        None. It's just used to update the circuit state
        """
        get_symbol_id: tuple = execute_query(DB_PATH, "select id from symbols where ticker = ?", (symbol, ))
        symbol_id: int = int(get_symbol_id[0]) if get_symbol_id else 0
        get_current_symbol_state: tuple = execute_query(DB_PATH, "select state from circuit_breaker_states where symbol_id = ?", (symbol_id, ))
        current_state: int = int(get_current_symbol_state[0]) if get_current_symbol_state else 0 #current state is closed by default

        #if current_state == 1:


        if success:
            if symbol_id:
                if current_state == 2:  #half open state successful API call
                    updated_state = Circuit_State.CLOSED.value
                    updated_failure_count = 0
                    updated_last_failure_time = None
                    logging.debug('Before the update: %s', execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))
                    execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ? where symbol_id = ?", (updated_failure_count, updated_last_failure_time, updated_state, symbol_id))
                    logging.debug('In the success block, after updating db record result is: %s', execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))
                    return
                else: #state is closed
                    logging.debug('Before the update: %s', execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))
                    execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ? where symbol_id = ?", (0, None, symbol_id))
                    logging.debug('In the success block, after updating db record result when previous state was closed is: %s', execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (symbol_id, )))
                    return
            else: 
                logging.debug('There is something wrong with the symbol id. The symbol id here is: %d', symbol_id)
                raise RecordNotFoundError('Symbol id does not exists!')
        else:
            #calculating time window to check if the last failure occured within the last 5 minutes
            failure_count_result, last_failure_time_result, existing_state, existing_cooldown_end_time = execute_query(DB_PATH, "select failure_count, last_fail_time, state, cooldown_end_time from circuit_breaker_states where symbol_id = ?", (symbol_id, )) 
            if last_failure_time_result: 
                last_failure_time_result = datetime.fromisoformat(last_failure_time_result)
                logging.debug('The last failure time returned from db query is: %s', last_failure_time_result)
            else: 
                logging.debug('Last failure time returned is None, so no errors have occured in the last 5 minutes and this is the first one.')
                failure_count = 1
                last_failure_time_result_= (datetime.now()).isoformat()
                updated_state = existing_state
                updated_cooldown_end_time = existing_cooldown_end_time

            time_difference_in_seconds = (datetime.now() - last_failure_time_result).total_seconds()
            if isinstance(last_failure_time_result, datetime): 
                last_failure_time_result = last_failure_time_result.isoformat()

            if time_difference_in_seconds > 300: #if last fail time more than 5 minutes, treat as new fail sequence
                logging.debug('Last failure time is > 5 minutes, so no errors have occured in the last 5 minutes and this is the first one.')
                failure_count = 1
                last_failure_time_result_= (datetime.now()).isoformat()
                updated_state = existing_state
                updated_cooldown_end_time = existing_cooldown_end_time
            
            else:
                failure_count = failure_count_result + 1

            if failure_count >= 3:
                updated_state = Circuit_State.OPEN.value
                updated_cooldown_end_time = (datetime.now() + timedelta(hours=1)).isoformat()

            else: 
                updated_state = existing_state
                updated_cooldown_end_time = existing_cooldown_end_time

            execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ?, cooldown_end_time = ? where symbol_id = ?", (failure_count, last_failure_time_result, updated_state, updated_cooldown_end_time, symbol_id))
            #execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ?, cooldown_end_time = ? where id = ?", (failure_count, current_timestamp_in_iso_format, ))


            # if current_state == 2:  #half open state unsuccessful API call
            #     updated_state = Circuit_State.OPEN.value
            #     updated_failure_count = 1
            #     updated_last_failure_time = datetime.now()
            #     updated_cooldown_end_time = updated_last_failure_time + timedelta(hours=1)
            #     execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ?, cooldown_end_time = ? where id = ?", (updated_failure_count, updated_last_failure_time.isoformat(), updated_state, updated_cooldown_end_time.isoformat(), symbol_id))

            # else:
            # #using 3 API failures occur within a 5-minute rolling window (as trigger condition)            

                

            #     new_updated_state = Circuit_State.CLOSED.value    
            #     if new_failure_count >= 3:
            #         new_updated_state = Circuit_State.OPEN.value
            #         new_cooldown_end_time = (datetime.now() + timedelta(hours=1)).isoformat()   
                    # update_db_record_result = execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ?, state = ?, cooldown_end_time = ? where id = ?", (new_failure_count, current_timestamp_in_iso_format, new_updated_state, new_cooldown_end_time, symbol_id))
                    # logging.debug('The result of updating db circuit breaker state is: %s', update_db_record_result)

                # else:
                #     updating_db_record = execute_query(DB_PATH, "update circuit_breaker_states set failure_count = ?, last_fail_time = ? where id = ?", (new_failure_count, current_timestamp_in_iso_format, symbol_id))
                #     logging.debug('The new failure count < 3, so the query result is: %s', updating_db_record)


    def _api_call_with_retry(self, symbol: str, market: str):
        url: str = f'{self.base_url}/query?function=TIME_SERIES_DAILY&symbol={symbol}.{market}&outputsize=5&apikey={self.api_key}'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        fetching_failure_counts = 0
        try:
            response: requests.Response = requests.get(url=url, headers=headers, timeout=10)
            response_code = response.status_code

            if response_code == 200:
                if "Error Message" in response.text:
                    logging.debug('The error is: %s', response.text)
                    logging.debug('Error in API response. Please check your parameters again')
                    #fetching_failure_counts += 1
                    return {}
                
                print('Reqeust has been successful') 
                return response.json()

            elif response_code == 429:
                fetching_failure_counts += 1
                wait_time = 65
                print(f'429 Error: Too many requests. Retry after {wait_time} seconds...')
                logging.debug('Api request returned 429 code. One retry attempt left after waiting %d seconds', wait_time)
                time.sleep(wait_time)
                second_api_call = self.fetch_daily_data(symbol, market)
                if not second_api_call:
                    logging.debug('Second retry attempt also failed. Returning empty dict.')
                    return {} 
                    #fetching_failure_counts += 1    

            elif response_code >= 500 and response_code < 600:
                logging.debug('Server error. Retrying after 10 seconds')
                time.sleep(10)
                first_api_retry_call = self.fetch_daily_data(symbol, market)
                if not first_api_retry_call:
                    logging.debug('First API retry call failed. Retrying after 20 seconds')
                    time.sleep(20)
                second_api_retry_call = self.fetch_daily_data(symbol, market)
                if not second_api_retry_call:
                    logging.debug('Second API retry call failed. Retrying after 40 seconds')
                    time.sleep(40)
                final_api_call = self.fetch_daily_data(symbol, market)
                if not final_api_call:
                    logging.debug("All the API retries have been made without a successful response. So, returning an empty dict") 
                    return {}

            else:
                fetching_failure_counts += 1 
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            fetching_failure_counts += 1
            print(f'Reques failed: {e}')
            raise

            #finally:
                #self._update_circuit_state(symbol=symbol)

        else:
            logging.debug('API calls not allowed as the circuit is open. Please try after some time')
            return {}


    def process_and_store(self, symbol: str, api_response: dict) -> dict:
        """
        Processing the obtained data, performing some validation checks and storing it in the database
        
        Args:
        symbol(str) - A string storing the ticker of the stock
        api_response(dict) - A dictionary containging the json value returned on successful call if fetch_data_daily function

        Returns:
        A dictionary containing the success message with operational stats about record insertion
        """

        #time_series_daily = api_response
        try:
            api_response_key = api_response.get('Time Series (Daily)')
        except KeyError as e:
            if 'Error Message' in api_response_key or 'Note' in api_response_key:
                return {
                    'status': 'error',
                    'message': e
                }
        else:
            logging.info('The symbol is: %s', symbol)
            symbol_table_query_result = execute_query(DB_PATH, "select id from symbols where ticker = ?", (symbol, ))
            if not symbol_table_query_result:
                #if ticker data not present in the symbols table, inserting it first
                insertion_query_result = execute_query(DB_PATH, "insert into symbols(ticker, company_name) values (?, ?)", (symbol, api_response['Meta Data']['2. Symbol']))
                if insertion_query_result:
                    symbol_id_from_symbols_table = execute_query(DB_PATH, "select id from symbols where ticker = ?", (symbol, ))
                    print(f'The symbols id is: {symbol_id_from_symbols_table}')
                else:
                    print('Data could not be inserted properly. Try again')

            else: 
                symbol_id_from_symbols_table = execute_query(DB_PATH, "select id from symbols where ticker = ?", (symbol, ))[0]
                print(f'The symbols id is: {symbol_id_from_symbols_table}')


            record_processed_count = 0
            skipped_rows_count = 0
            records: list[tuple] = []

            for date_key, value in api_response_key.items():
                record_processed_count += 1
                open_string, high_string, low_string, close_string, volume_string = value.values()
                open, high, low, close, volume = float(open_string), float(high_string), float(low_string), float(close_string), float(volume_string)
                timestamp = datetime.strptime(f'{date_key} 00:00:00', '%Y-%m-%d %H:%M:%S')
                iso_timestamp = datetime.strptime(timestamp.isoformat(), "%Y-%m-%dT%H:%M:%S")
                
                try:
                    if high >= low and high >= open and high >= close and low <= open and low <= close and volume >= 0 and iso_timestamp <= datetime.now():
                        records.append((symbol_id_from_symbols_table, iso_timestamp.isoformat(), open, close, high, low, volume))
                    else:
                        logging.warning(f'Skipped malformed record for {iso_timestamp}: {e}')
                        continue

                except (TypeError, ValueError) as e:
                    print(f'Skipping malformed data for timestamp: {iso_timestamp} - {e}')
                    skipped_rows_count += 1

            if not records: 
                print('No valid records to insert in db')
                return
            
            new_data_insertion_query_result = insert_bulk_data(DB_PATH, records)
            return {
                    'status': 'Success',
                    'records_processed': record_processed_count,
                    'records_inserted': new_data_insertion_query_result,
                    'errors': 0
                }
                        
    def load_as_dataframe(self, csv_path):
        """Load the downloaded CSV data as Pandas dataframe"""
        if not csv_path:
            raise FileNotFoundError('The file could not be found')
        with open(csv_path, 'r', encoding='utf-8') as file:
            # pd.read_csv(csv_path)
            for chunk in pd.read_csv(file, chunksize=1000):
                yield chunk

                

result_class = FinancialDataDownloader()

# data = result_class.fetch_daily_data(symbol='NMDC', market='BSE')
# storing_data_result = result_class.process_and_store('NMDC', data)
# print(storing_data_result)
#print(execute_query(DB_PATH, "update circuit_breaker_states set state = ? where symbol_id = ?", (Circuit_State.OPEN.value, 2)))
#print(execute_query(DB_PATH, "insert into circuit_breaker_states(symbol_id, failure_count, state) values(?, ?, ?)", (2, 0, Circuit_State.HALF_OPEN.value)))
#print(result_class.fetch_daily_data('TCS'))

#print(execute_query(DB_PATH, "select * from circuit_breaker_states where symbol_id = ?", (2, )))

# myResult = execute_query(DB_PATH, "select * from symbols where id = ?", (2, ))
# print(myResult)

# print(f'The tables currently are: {list_tables(DB_PATH)}')