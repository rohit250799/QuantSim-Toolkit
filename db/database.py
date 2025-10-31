import os
import sqlite3
from dotenv import load_dotenv
#from config.config_manager import load_config

load_dotenv()

#load_config()

DB_PATH = os.getenv('DB_PATH', 'QuantSim-Toolkit/db/quantsim.db')
print(f'The db path is: {DB_PATH}')

def init_db(db_path: str = DB_PATH):
    """Initialize the database and create directories if necessary"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    if conn: 
        print('Successfully connected to the database')
    else: 
        raise ConnectionError('Could not connect to the database!')
    conn.close()

def list_tables(db_path: str = DB_PATH):
    """Return a list of all tables present in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def execute_query(db_path: str, query: str, params: tuple = ()):
    """Execute queries on the database and return results if any"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results

def create_table_and_insert_values():
    "Function to test db integration by creating table and inserting values"
    try:
        init_db(db_path=DB_PATH)
    except ConnectionError: 
        print('There has been a problem connecting to the database')
    else:
        query: str = 'SELECT name FROM sqlite_master '
        result = execute_query(DB_PATH, query)
        print(result)    

price_data_table_creation_query: str = "create table if not exists price_data(id INTEGER PRIMARY KEY, " \
"symbols_id INTEGER, timestamp TEXT NOT NULL, open REAL,close REAL, high REAL, low REAL, volume int, " \
"created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (symbols_id) REFERENCES symbols(id));"

api_logs_table_creation_query: str = "create table if not exists api_logs(id int PRIMARY KEY, symbol TEXT, " \
"endpoint TEXT, status_code int, response_time_ms int, timestamp TEXT DEFAULT CURRENT_TIMESTAMP);"

price_data_table_res = execute_query(DB_PATH, price_data_table_creation_query)
api_logs_table_res = execute_query(DB_PATH, api_logs_table_creation_query)

print(list_tables(DB_PATH))

print(execute_query(DB_PATH, 'select * from price_data;'))