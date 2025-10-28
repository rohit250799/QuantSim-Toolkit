import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH=os.getenv('DB_PATH', 'QuantSim-Toolkit/db/quantsim.db')

conn = sqlite3.connect(DB_PATH)
curr = conn.cursor()

curr.execute('CREATE TABLE IF NOT EXISTS stocks(timestamp, open, high, low, close, volume)')

def get_all_created_table_names(query: str = 'SELECT name from sqlite_master'):
    """Returns the names of all the created tables in the db"""
    res = curr.execute(query)
    return res.fetchall()

result = get_all_created_table_names()
print(result)
