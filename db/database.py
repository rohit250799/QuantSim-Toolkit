from typing import List, Tuple, Any
import os
import sqlite3
import logging
from dotenv import load_dotenv
from pathlib import Path
#from config.config_manager import load_config

load_dotenv()
PROD_DB_PATH = "db/quantsim.db"

logging.basicConfig(filename='logs/db_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

#load_config()

def init_db(db_path: str = PROD_DB_PATH) -> None:
    """Initialize the database and create directories if necessary"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    if conn: 
        print('Successfully connected to the database')
    else: 
        raise ConnectionError('Could not connect to the database!')
    conn.close()

def list_tables(db_path: str = PROD_DB_PATH) -> List[str]:
    """Return a list of all tables present in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def execute_query(db_path: str, query: str, params: tuple[Any, ...] = ()) -> Tuple[Any, ...]:
    """Execute queries on the database and return results if any"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try: 
        cursor.execute(query, params)
        #checking if the query is a select type query
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results if results else tuple()
        else:
            conn.commit()
            return tuple()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        logging.debug('There has been a database error while query execution: %s', e)
        raise #re-reising exception after printing and logging 
    finally:
        conn.close()

def insert_bulk_data(db_path: str, records: List[Tuple[Any, ...]]) -> int:
    """
    Insert multiple rows in the database with transaction safety. 
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    records_inserted = 0

    try:
        conn.execute("begin transaction;")
        bulk_insert_query: str = """
        insert or ignore into price_data (symbols_id, timestamp, open, close, high, low, volume) values
        (?, ?, ?, ?, ?, ?, ?)
        """

        #bulk insert with executemany
        cursor.executemany(bulk_insert_query, records)

        conn.commit()
        records_inserted = cursor.rowcount if cursor.rowcount != -1 else len(records)
        logging.info('Successfully inserted %d new records with duplicates ignored', records_inserted)

    except Exception as e:
        conn.rollback()
        logging.error('Transaction rolled back due to error: %s', e)

    finally:
        conn.close()
    return records_inserted

def create_table_and_insert_values() -> None:
    "Function to test db integration by creating table and inserting values"
    try:
        init_db(db_path=PROD_DB_PATH)
    except ConnectionError: 
        print('There has been a problem connecting to the database')
    else:
        query: str = 'SELECT name FROM sqlite_master '
        result = execute_query(PROD_DB_PATH, query)
        print(result)    

symbol_table_creation_query: str = "create table if not exists symbols (id integer primary key, ticker text unique not null, " \
"company_name text, created_at text default CURRENT_TIMESTAMP);"

price_data_table_creation_query: str = "create table if not exists price_data(id INTEGER PRIMARY KEY, " \
"symbols_id INTEGER, timestamp TEXT NOT NULL, open REAL,close REAL, high REAL, low REAL, volume int, " \
"created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(symbols_id, timestamp), FOREIGN KEY (symbols_id) REFERENCES symbols(id));"

api_logs_table_creation_query: str = "create table if not exists api_logs(id int PRIMARY KEY, symbol TEXT, " \
"endpoint TEXT, status_code int, response_time_ms int, timestamp TEXT DEFAULT CURRENT_TIMESTAMP);"

circuit_breaker_states_table_creation_query: str = "create table if not exists circuit_breaker_states(id INTEGER PRIMARY KEY, " \
"symbol_id INTEGER, failure_count INTEGER, last_fail_time TEXT, state INTEGER NOT NULL, cooldown_end_time TEXT DEFAULT NULL)"

error_metrics_table_creation_query: str = "create table if not exists error_metrics(id INTEGER PRIMARY KEY, timestamp TEXT, error_type INTEGER, error_message TEXT, resolution INTEGER)"

alerts_table_creation_query: str = "create table if not exists alerts(id INTEGER PRIMARY KEY, timestamp TEXT, alert_type INTEGER, symbol TEXT, message TEXT, severity INTEGER, acknowledged INTEGER)"

api_call_metrics_table_creation_query: str = "create table if not exists api_call_metrics(id INTEGER PRIMARY KEY, timestamp TEXT, symbol TEXT, endpoint TEXT, status_code INTEGER, response_time_ms INTEGER, success INTEGER, error_message TEXT)"

#create_index_for_timestamp_field_in_api_call_metrics = execute_query(DB_PATH, "CREATE INDEX idx_timestamp on api_call_metrics(timestamp)")
#alerts_table_res = execute_query(DB_PATH, alerts_table_creation_query)
#api_call_metrics_table_res = execute_query(DB_PATH, api_call_metrics_table_creation_query)

#print(list_tables(DB_PATH))

#print(execute_query(DB_PATH, 'select * from error_metrics;'))
