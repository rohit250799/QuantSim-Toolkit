from src.modules.stock_data_downloader import FinancialDataDownloader, Circuit_State
from db.database import execute_query, symbol_table_creation_query, circuit_breaker_states_table_creation_query
from src.custom_errors import RecordNotFoundError
from helper_functions import make_open_circuit_breaker_state_table_row, can_call_api

from collections.abc import Generator
from typing import Any
import logging
import os
import pytest 
import sqlite3
#import tempfile
from datetime import datetime, timedelta

logging.basicConfig(filename='logs/pytest_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

@pytest.fixture(scope="function")
def test_db_connection() -> Generator[Any, Any, Any]:
    """
    Each test gets a fresh transaction and rolls it back.
    Pure sqlite3 and standard library only.
    """
    # Establishing single in memory connection - guarantees isolation from disk DB and other tests
    conn = sqlite3.connect(':memory:')
    # Passing the Active connection object to the test function
    yield conn
    # close connection after test, destroying the in-memory DB
    conn.close()



class TestFinancialDataDownloader:
    """Testing all the functions of the financial data downloader class"""

    def test_initialization(self) -> None:
        api_key_obtained = os.environ.get('ALPHA_VANTAGE_API_KEY', 'key not found')
        if api_key_obtained == 'key_not_found':
            logging.debug('In test market data production file - failed to obtain api key from environment variables. API Key obtained: %s', api_key_obtained)
            raise KeyError('Key not found in the environment variables')
        instance = FinancialDataDownloader()
        assert isinstance(instance, FinancialDataDownloader)

        assert instance.api_key == api_key_obtained
        assert instance.base_url == 'https://www.alphavantage.co'

        logging.info('The assertions made on creation of financial data downloader are all correct - the api key and base url are all rightly fetched')

    def test_table_creation(self, test_db_connection: Any) -> None:
        """Test the creation of a new table in the in-memory database while performing unit tests"""
        table_name = 'my_new_symbol_table'
        execute_query(test_db_connection, f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, symbol TEXT);")
        created_tables = execute_query(test_db_connection, "SELECT name FROM sqlite_master WHERE type='table';")
        logging.debug('The newly created tables from test table creation function are: %s', execute_query(test_db_connection, "SELECT name FROM sqlite_master WHERE type='table';"))
        assert('my_new_symbol_table',) in created_tables

    def test_data_insertion(self, test_db_connection: Any) -> None:
        """Tests the insertion of data in the newly created table""" 
        table_name = 'my_new_symbol_table'
        execute_query(test_db_connection, f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, symbol TEXT);")
        execute_query(test_db_connection, f"insert into {table_name}(symbol) values(?)", ('TCS',))
        logging.info('The symbol to be inserted is: TCS')
        insertion_query_fetch_result = execute_query(test_db_connection, "select * from my_new_symbol_table where symbol = ?", ('TCS', ))
        logging.debug('The insertion query fetch result is: %s', insertion_query_fetch_result)
        assert insertion_query_fetch_result == ((1, 'TCS'), )

    def test_api_calls_not_allowed(self, test_db_connection: Any) -> None:
        """
        API calls are alloweed only when the state in the circuit breaker states table is Closed or Half-Open(single call). In this test, we will make sure that when the state
        is open, no API calls are allowed. API calls will be allowed only if state is Closed or Half-Open
        """
        execute_query(test_db_connection, circuit_breaker_states_table_creation_query)

        open_row = make_open_circuit_breaker_state_table_row(
            id=1, symbol_id=1, failure_count=3, last_fail_time=None,
            state=1, 
            cooldown_end_time=None
        )

        execute_query(
            test_db_connection,
            "INSERT INTO circuit_breaker_states VALUES (?, ?, ?, ?, ?, ?)",
            open_row
        )

        state = execute_query(
            test_db_connection,
            "SELECT state FROM circuit_breaker_states WHERE symbol_id = ? LIMIT 1",
            (1,)
        )[0][0]

        # OPEN state → API must NOT be allowed
        assert can_call_api(state) is False
        logging.info("Assertion correct: OPEN state (1) → API calls NOT allowed")

        closed_row = make_open_circuit_breaker_state_table_row(
            id=2, symbol_id=2, failure_count=0, last_fail_time=None,
            state=0, 
            cooldown_end_time=None
        )

        execute_query(
            test_db_connection,
            "INSERT INTO circuit_breaker_states VALUES (?, ?, ?, ?, ?, ?)",
            closed_row
        )

        state = execute_query(
            test_db_connection,
            "SELECT state FROM circuit_breaker_states WHERE symbol_id = ? LIMIT 1",
            (2,)
        )[0][0]

        assert can_call_api(state) is True
        logging.info("Assertion correct: CLOSED state (0) → API calls allowed")



    # def test_circuit_state_updation_based_on_api_response(self, test_db_connection):
    #     """
        
    #     """
    #     pass


    
    # @pytest.fixture
    # def existing_symbol(self):
    #     return "TCS"
    
    # @pytest.fixture
    # def missing_symbol(self):
    #     return 'B'
    
    