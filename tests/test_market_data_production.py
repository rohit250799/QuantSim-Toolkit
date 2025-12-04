from src.modules.stock_data_downloader import FinancialDataDownloader, Circuit_State
from db.database import execute_query, symbol_table_creation_query, price_data_table_creation_query, list_tables
from src.custom_errors import RecordNotFoundError

import logging
import os
import pytest 
import sqlite3
import tempfile

logging.basicConfig(filename='logs/pytest_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')


class TestFinancialDataDownloader:
    """Testing all the functions of the financial data downloader class"""

    @pytest.fixture(scope="function")
    def test_db_path(self):
        """Used to provide the test database path for the underneath functions"""
        #option A - for unit tests
        return ":memory:"
    
        #option B - for the integration tests
        # with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
        #     yield tmp.name
        # os.unlink(tmp.name) # Cleans up the file after the test

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

    def test_table_creation(self, test_db_path):
        """Unit test to test the creation of a table inside the database using a manual query"""
        table_name = 'my_new_symbol_table'
        execute_query(test_db_path, f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, symbol TEXT);")
        created_tables = execute_query(test_db_path, "SELECT name FROM sqlite_master WHERE type='table';")
    
        assert (table_name,) in created_tables

    @pytest.fixture
    def existing_symbol(self):
        return "TCS"
    
    @pytest.fixture
    def missing_symbol(self):
        return 'B'
    
    def test_insert_order(self, test_db_path):
        execute_query(test_db_path, symbol_table_creation_query)
        #created_tables_list = execute_query(test_db_path, list_tables)
        created_tables_list = list_tables(test_db_path)
        #symbols_table_fetching_data = execute_query(test_db_path, "select * from symbols;")
        logging.debug('The created tables are: %s', created_tables_list)
        return

    