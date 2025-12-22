import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from db.database import execute_query
from db.db_queries import set_circuit_state_query
from src.quant_enums import Circuit_State

from src.data_loader.data_loader import DataLoader
from src.custom_errors import CircuitOpenStateError

logging.basicConfig(filename='logs/circuit_breaker_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

current_timestamp = int(datetime.now().timestamp())


class CircuitBreaker:

    def __init__(self, data_loader: DataLoader) -> None:
        self._data_loader = data_loader

    def check_circuit_state(self, ticker: str) -> bool:
        """
        Used to check the current state of the circuit for a particular ticker
        
        Args: ticker (str) - ticker (stock symbol) of the stock for which to check the state
        Returns: True if the circuit state is CLosed or Half-Open (signifying API calls can be made). False if state is Open
        Raises: Exception if the State is close and notifies the user to try after some time
        """
        data_loader = self._data_loader
        circuit_breaker_state_record = _, record_state, _, _, record_cooldown_end_time = data_loader.get_circuit_state(ticker=ticker)
        #current_circuit_state = data_loader.get_circuit_state(ticker)
        logging.info('The current state of the circuit is: %s and the cooldown end time is: %s', record_state, record_cooldown_end_time)
        #logging.debug('The current circuit state is: %s', current_circuit_state)
        logging.debug('The record to be output is: %s', circuit_breaker_state_record)
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
        current_unix_timestamp = int(timestamp.timestamp())
        if record_state == Circuit_State.OPEN.value and current_unix_timestamp < record_cooldown_end_time:
            logging.info('Circuit is currently in Open state! Try again after 1 hour')
            raise CircuitOpenStateError('Circuit is currently in open state! Try again after 1 hour')
        elif record_state == Circuit_State.OPEN.value and current_unix_timestamp > record_cooldown_end_time:
            logging.info('Resetting circuit to Half-Open state for ticker: %s', ticker)
            self.reset_circuit_breaker(ticker=ticker)
            return True
        else:
            logging.info('Circuit is not in Open state! So, API calls are allowed')
            return True
            
        
    def handle_failure(self, ticker: str, consecutive_failures: int = 3, current_timestamp: int = current_timestamp) -> None:
        """
        Handles failure of the API call, based on the threshold for failure.
        If failure count exceeds threshold in a specified time (5 minutes in this case) - the circuit state transitions to Open. Else, it remains Closed.
        """
        if consecutive_failures > 3:
            logging.info('Consecutive API calls failed > 3 times for the ticker: %s in 5 minutes. So, opening the circuit for 1 hour.', ticker)
            # current_time = datetime.now(ZoneInfo("Asia/Kolkata"))
            # current_time_unix = int(current_time.timestamp())
            current_timestamp_dt = datetime.fromtimestamp(current_timestamp, tz=timezone.utc)
            one_hour_later_timestamp = current_timestamp_dt + timedelta(hours=1)
            one_hour_later_timestamp_unix = int(one_hour_later_timestamp.timestamp())
            self._data_loader.set_circuit_state(ticker=ticker, state=Circuit_State.OPEN.value, failure_count=consecutive_failures, last_fail_time=current_timestamp, cooldown_end_time=one_hour_later_timestamp_unix)
            logging.info('The circuit has been opened!')
            return
        logging.info('Since failure count < 3, the circuit state remains Closed')
        return

    def handle_success(self, ticker: str) -> None:
        """
        If the current state is Open or Half-Open for a ticker, this function flips the state back to Closed.
        """
        _, current_state, _, _, _ = self._data_loader.get_circuit_state(ticker=ticker)
        logging.info('The current state is: %s', current_state)
        
        failure_count = None
        cooldown_end_time = None
        if current_state == Circuit_State.OPEN.value or current_state == Circuit_State.HALF_OPEN.value:
            current_state = Circuit_State.CLOSED.value
            failure_count = 0
            logging.debug('Flipping the state of the ticker: %s to Closed', ticker)

            self._data_loader.set_circuit_state(ticker, current_state, failure_count, None, cooldown_end_time)

        logging.debug('After flipping, the current state of the ticker is: %s', self._data_loader.get_circuit_state(ticker))
        return
        

    def reset_circuit_breaker(self, ticker: str) -> None:
        """
        Handles transition from Open to Half Open when the cooldown time has expired
        """
        _, current_state_of_ticker, _, _, cooldown_end_time = self._data_loader.get_circuit_state(ticker=ticker)
        current_time = datetime.now(ZoneInfo('Asia/Kolkata'))
        unix_current_time = int(current_time.timestamp())

        if current_state_of_ticker == 'OPEN' and unix_current_time > cooldown_end_time:
            logging.info('Since the current state of the circuit is: %s, flipping it to Half-Open', current_state_of_ticker)
            self._data_loader.set_circuit_state(ticker=ticker, state=Circuit_State.HALF_OPEN.value, failure_count=0, last_fail_time=None, cooldown_end_time=None)
            logging.debug('After updation, the current state of the record is: %s', self._data_loader.get_circuit_state(ticker))
            return
        
        logging.info('The circuit state of the ticker is not Open!')
        return
