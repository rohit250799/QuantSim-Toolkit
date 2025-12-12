import pytest
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Generator, Any

from helper_functions import (
    make_open_circuit_breaker_state_table_row, 
    make_price_data_row, make_symbol_row, 
    can_call_api
)

# Define the schema creation SQL. This should mirror your actual database schema.

SYMBOL_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

PRICE_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS price_data (
    id INTEGER PRIMARY KEY,
    symbols_id INTEGER,
    timestamp TEXT NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbols_id, timestamp),
    FOREIGN KEY (symbols_id) REFERENCES symbols(id)
);
"""

API_LOGS_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    endpoint TEXT,
    status_code INTEGER,
    response_time_ms INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CIRCUIT_BREAKER_STATES_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS circuit_breaker_states (
    id INTEGER PRIMARY KEY,
    symbol_id INTEGER,
    failure_count INTEGER,
    last_fail_time TEXT,
    state INTEGER NOT NULL,
    cooldown_end_time TEXT DEFAULT NULL
);
"""

ERROR_METRICS_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS error_metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    error_type INTEGER,
    error_message TEXT,
    resolution INTEGER
);
"""

ALERTS_TABLE_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    alert_type INTEGER,
    symbol TEXT,
    message TEXT,
    severity INTEGER,
    acknowledged INTEGER
);
"""

API_CALL_METRICS_DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_call_metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    symbol TEXT,
    endpoint TEXT,
    status_code INTEGER,
    response_time_ms INTEGER,
    success INTEGER,
    error_message TEXT
);
"""

@pytest.fixture(scope="session")
def in_memory_db() -> Generator[sqlite3.Connection, Any, None]:
    """
    Sets up a clean, in-memory SQLite database connection for the entire test session.
    """
    # Connecting to an in-memory database
    # ':memory:' means the database exists only in RAM and is destroyed when the connection is closed.
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.executescript(
        f"""
        {SYMBOL_DATA_SCHEMA}
        {PRICE_DATA_SCHEMA}
        {API_LOGS_DATA_SCHEMA}
        {CIRCUIT_BREAKER_STATES_DATA_SCHEMA}
        {ERROR_METRICS_DATA_SCHEMA}
        {ALERTS_TABLE_DATA_SCHEMA}
        {API_CALL_METRICS_DATA_SCHEMA}
        """
    )
    conn.commit()

    symbol_record = make_symbol_row()
    price_data_record = make_price_data_row()
    open_circuit_breaker_record = make_open_circuit_breaker_state_table_row()
    closed_circuit_breaker_record = make_open_circuit_breaker_state_table_row(id=2, symbol_id=2, failure_count=0, last_fail_time=None, state=0, cooldown_end_time=None)

    cursor.execute("BEGIN")

    cursor.execute("insert into symbols values(?, ?, ?, ?)", symbol_record)

    cursor.execute("insert into price_data values(?, ?, ?, ?, ?, ?, ?, ?, ?)", price_data_record)

    circuit_breaker_states_insertion_sql = "insert into circuit_breaker_states values (?, ?, ?, ?, ?, ?)"
    circuit_breaker_states_records_to_insert = [open_circuit_breaker_record, closed_circuit_breaker_record]
    cursor.executemany(circuit_breaker_states_insertion_sql, circuit_breaker_states_records_to_insert)
    conn.commit()

    yield conn

    # Teardown - Closing the connection and thus destroy the in-memory db
    conn.close()

# Example fixture to fetch the data directly, ready for analysis functions
@pytest.fixture(scope="function")
def tcs_test_data(in_memory_db: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetches the seeded TCS data as a clean Pandas DataFrame for a test function.
    """
    query = "SELECT * FROM prices WHERE symbol = 'TCS' ORDER BY timestamp"
    df = pd.read_sql(query, in_memory_db, parse_dates=['timestamp'], index_col='timestamp')
    
    # Ensure all required columns are clean float32 for testing efficiency
    df['close'] = df['close'].astype(np.float32)
    return df