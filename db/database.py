from typing import List, Tuple, Any
import os
import sqlite3
import logging
from dotenv import load_dotenv

load_dotenv()
PROD_DB_PATH = "db/quantsim.db"

logger = logging.getLogger("db")

def init_db(db_path: str = PROD_DB_PATH) -> None:
    """Initialize the database and create directories if necessary"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn: sqlite3.Connection = sqlite3.connect(db_path)
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

def get_prod_conn(db_path: str = PROD_DB_PATH) -> sqlite3.Connection:
    try: 
        conn: sqlite3.Connection = sqlite3.connect(db_path)
    except ConnectionError as e:
        logging.debug('There has been a Connection error while connecting to the quantsim database, Error: %s', e)
        raise
    else:
        logging.info('Successfully connected to thhe database. Now, returning the connection object!')
        return conn

def execute_query(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> Tuple[Any, ...]:
    """
    Execute queries on an existing connection object.
    It commits non-SELECT queries and fetches all results for SELECT statements
    """
    try: 
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return tuple(results)
        else: #Involves a Write / Schema operation - so, commiting the change is necessary
            conn.commit()
            return tuple()
    except sqlite3.Error as e:
        logging.debug('Database error duting query execution: %s', e)
        raise

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

#for timestamp, epoch unit is: unix epoch seconds


