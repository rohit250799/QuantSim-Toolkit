import sqlite3
from sqlite3 import Connection
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from db.database import get_prod_conn
from src.quant_enums import LogLevel
from db.db_queries import (
    list_all_existing_tables_query,
    price_data_table_creation_query,
    symbol_table_creation_query,
    circuit_breaker_states_table_creation_query,
    system_logs_table_creation_query,
    validation_log_table_creation_query, 
    system_config_table_creation_query
)

logging.basicConfig(filename='logs/db_operations_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

class DataLoader:
    """
    Provides all methods necessary to abstract all DB I/O operations, schema management(migrations)
    and data formatting(like date conversion)

    Must: hold the active SQLite connection and cursor as attributes
    """
    def __init__(self, db_conn: None | Connection = None) -> None:
        self.prod_db_connection = db_conn if db_conn is not None else get_prod_conn()
        self._run_migrations()

    def get_all_existing_tables(self):
        """Get the names of all the existing tables in the db"""
        conn = self.prod_db_connection
        cursor = conn.cursor()

        cursor.execute(list_all_existing_tables_query)
        tables = cursor.fetchall()

        for table in tables:
            logging.debug('Table name: %a', table[0])
        
        return

    def _run_migrations(self):
        """Handles one-time cleanup and schema creation"""
        conn = self.prod_db_connection
        try:
            cursor = conn.cursor()

            cursor.execute('BEGIN TRANSACTION')
            
            cursor.execute(price_data_table_creation_query)
            cursor.execute(circuit_breaker_states_table_creation_query)
            cursor.execute(symbol_table_creation_query)
            cursor.execute(system_logs_table_creation_query)
            cursor.execute(validation_log_table_creation_query)
            cursor.execute(system_config_table_creation_query)

            conn.commit()
        except sqlite3.Error as e:
            logging.debug('An error occured: %s', e)
            conn.rollback()
        
        else:
            logging.debug('All the mentioned tables have been created in the db')
            self.insert_log_entry(level=LogLevel.WARNING.value, source='Data loader module', message='Created new schemas into the db')


    def insert_log_entry(self, level: LogLevel, source: str, message: str, **kwargs):
        """Insert logs into the system_logs table for every database operation"""
        conn = self.prod_db_connection
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
        unix_timestamp_value = int(timestamp.timestamp())
        level_value = level
        source_value = source
        message_value = message
        ticker_value = kwargs['ticker'] if 'ticker' in kwargs else None
        api_status_code_value = kwargs['api_status_code'] if 'api_status_code' in kwargs else None
        response_time_ms_value = kwargs['response_time_ms'] if 'response_time_ms' in kwargs else None 

        system_logs_table_record_query: str = """
            insert into system_logs(
                timestamp, level, source, message, ticker, api_status_code, response_time_ms
            ) values(
                ?, ?, ?, ?, ?, ?, ?
            )
        """

        try:
            cursor = conn.cursor()
            cursor.execute(system_logs_table_record_query, (unix_timestamp_value, level_value, source_value, message_value, ticker_value, api_status_code_value, response_time_ms_value))
            conn.commit()
        except sqlite3.Error as e:
            logging.debug('An error occured: %s', e)
            raise ValueError('Error raised in record insertion: %s. Please fix it first.', e)
        else:
            last_record_id = cursor.lastrowid
            cursor.execute("select * from system_logs where id = ?", (last_record_id, )) 
            last_record = cursor.fetchone()
            logging.info('Record: %s has been successfully inserted into the db', last_record)
            return




my_dl = DataLoader()
print(my_dl.get_all_existing_tables())

