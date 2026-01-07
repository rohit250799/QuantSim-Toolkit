from collections.abc import Generator
from typing import Any
import logging
import os
import pytest 
import sqlite3
from datetime import datetime, timedelta

from db.database import execute_query
from db.db_queries import circuit_breaker_states_table_creation_query
from src.adapters.api_adapter import ApiAdapter
from tests.helper_functions import can_call_api
from tests.conftest import fetch_scalar

logger = logging.getLogger("errors")

class TestFinancialDataDownloader:
    """Testing all the functions of the financial data downloader class"""

    def test_initialization(self, in_memory_db: Any) -> None:
        api_key_obtained = os.environ.get('ALPHA_VANTAGE_API_KEY', 'key not found')
        if api_key_obtained == 'key_not_found':
            logger.debug('In test market data production file - failed to obtain api key from environment variables. API Key obtained: %s', api_key_obtained)
            raise KeyError('Key not found in the environment variables')
        instance = ApiAdapter()

        assert instance.api_key == api_key_obtained
        assert instance.base_url == 'https://www.alphavantage.co'

        logger.info('The assertions made on creation of API Adapter are all correct - the api key and base url are all rightly fetched')

    def test_new_table_creation(self, in_memory_db: Any) -> None:
        """Test the creation of a new table in the in-memory database while performing unit tests"""
        conn = in_memory_db
        table_name = 'my_new_testing_table'
        execute_query(conn, f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, symbol TEXT);")
        created_tables = execute_query(conn, "SELECT name FROM sqlite_master WHERE type='table';")
        all_table_names = [row["name"] for row in created_tables]
        logger.debug('The newly created tables from test table creation function are: %s', all_table_names)
        assert table_name in all_table_names

    def test_data_insertion(self, in_memory_db: Any) -> None:
        """Tests the insertion of data in the newly created table""" 
        table_name = 'my_new_symbol_table'
        conn = in_memory_db

        execute_query(conn, f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, symbol TEXT);")
        execute_query(conn, f"INSERT INTO {table_name}(symbol) VALUES (?)", ('TCS',))
        logger.info("Inserted symbol: TCS")

        rows = execute_query(
            conn,
            "SELECT * FROM my_new_symbol_table WHERE symbol = ?",
            ('TCS',)
        )

        logger.debug("Insertion fetch result: %s", rows)

        # Expecting exactly one row
        assert len(rows) == 1
        row = rows[0]

        assert row["id"] == 1
        assert row["symbol"] == "TCS"

    def test_api_calls_not_allowed(self, in_memory_db: Any) -> None:
        """
        API calls are alloweed only when the state in the circuit breaker states table is Closed or Half-Open(single call). In this test, we will make sure that when the state
        is open, no API calls are allowed. API calls will be allowed only if state is Closed or Half-Open
        """
        conn = in_memory_db
        execute_query(conn, circuit_breaker_states_table_creation_query)
        state = fetch_scalar(
            conn,
            "SELECT state FROM circuit_breaker_states WHERE ticker = ?",
            ('TCS',)
        )
        logger.info('The state returned from the tests is: %s', state)

        # OPEN state → API must NOT be allowed
        assert can_call_api(state) is False
        logger.info("Assertion correct: OPEN state (1) → API calls NOT allowed")

        state = fetch_scalar(
            conn,
            "SELECT state FROM circuit_breaker_states WHERE ticker = ?",
            ('INFY',)
        )

        #closed state, allowing API calls
        assert can_call_api(state) is True
        logger.info("Assertion correct: CLOSED state (0) → API calls allowed")

    