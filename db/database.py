from typing import List, Tuple, Any
import os
import sqlite3
import logging
from dotenv import load_dotenv
from pathlib import Path

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

def get_prod_conn(db_path: Path) -> sqlite3.Connection:
    """
    Fetches the connection to the production Database

    Returns - the sqlite3.Connection to the production database
    """
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
    except sqlite3.Error as e:
        logging.debug(
            "Connection error while connecting to DB at %s: %s",
            db_path,
            e,
        )
        raise
    else:
        logging.info("Connected to database at %s", db_path)
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

def get_db_path() -> Path:
    """
    Serves as the Deterministic DB Location to handle the following:
    - CI / Github codespaces: auto-created
    - Local: predictable
    - Prod: overridable via env
    """

    env_path = os.getenv("DB_PATH")
    if env_path:
        return Path(env_path)
    
    return Path('db/quantsim.db')

#for timestamp, epoch unit is: unix epoch seconds


