import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'QuantSim-Toolkit/db/quantsim.db')
print(f'The db path is: {DB_PATH}')

def init_db(db_path: str):
    """Initialize the database and create directories if necessary"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.close()

def list_tables(db_path: str):
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
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results

if __name__ == '__main__':
    db_file = 'QuantSim-Toolkit/db/quantsim.db'

    init_db(db_file)
    execute_query(db_file, "" \
    "CREATE TABLE IF NOT EXISTS symbols (id INTEGER PRIMARY KEY, ticker TEXT UNIQUE NOT NULL, company_name TEXT, " \
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

    print("Tables:", list_tables(db_file))
    print("Symbols:", execute_query(db_file, "SELECT * FROM symbols;"))