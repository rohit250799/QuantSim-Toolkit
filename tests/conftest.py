import pytest
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Generator, Any, Tuple

# --- 1. MOCKING DEPENDENCIES ---
# Define the mock data helper functions here or ensure they are imported.
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
one_day_previous_current_timestamp = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
cooldown_end_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

def make_symbol_row(id: int = 1, ticker:str = "TCS", company_name: str= "TCS", created_at: str= current_timestamp) -> Tuple[int, str, str, str]:
    """A record for the symbols table to test with"""
    return (id, ticker, company_name, created_at)

def make_price_data_row(id: int = 1, symbols_id: int = 1, timestamp: str = one_day_previous_current_timestamp, open: float = 122.43, close: float = 146.81, high: float = 151.04, low: float = 119.63, volume: int = 154, created_at: str = current_timestamp) -> Tuple[int, int, str, float, float, float, float, int, str]:
    """A record for the price data table"""
    return (id, symbols_id, timestamp, open, close, high, low, volume, created_at)

def make_open_circuit_breaker_state_table_row(id: int = 1, symbol_id: int = 1, failure_count: int = 5, last_fail_time: str | None = current_timestamp, state: int = 1, cooldown_end_time: str | None = cooldown_end_time) -> Tuple[int, int, int, str | None, int | None, str | None]:
    """A record for the circuit breaker state table"""
    return (id, symbol_id, failure_count, last_fail_time, state, cooldown_end_time)

# --- 2. DATABASE SCHEMA DEFINITION (DDL) ---

DB_SCHEMA_DDL = f"""
-- Table to hold the list of trading instruments
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table to hold the OHLCV price data
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

-- Table for tracking API failure state (Circuit Breaker)
CREATE TABLE IF NOT EXISTS circuit_breaker_states (
    id INTEGER PRIMARY KEY,
    symbol_id INTEGER UNIQUE,
    failure_count INTEGER,
    last_fail_time TEXT,
    state INTEGER NOT NULL, -- 0: Closed (OK), 1: Open (Failing), 2: Half-Open (Testing)
    cooldown_end_time TEXT DEFAULT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);

-- Additional operational tables
CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    endpoint TEXT,
    status_code INTEGER,
    response_time_ms INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS error_metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    error_type INTEGER,
    error_message TEXT,
    resolution INTEGER
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    alert_type INTEGER,
    symbol TEXT,
    message TEXT,
    severity INTEGER,
    acknowledged INTEGER
);

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

# --- 3. SESSION SCOPED FIXTURE: Setting up db structure once (Baseline) ---

@pytest.fixture(scope="session")
def in_memory_db() -> Generator[sqlite3.Connection, Any, None]:
    """
    Sets up a clean, in-memory SQLite database connection for the entire test session.
    Only runs once. Provides connection.
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Creating all schemas
    cursor.executescript(DB_SCHEMA_DDL)

    # Seeding baseline data
    symbol_record_tcs = make_symbol_row(id=1, ticker="TCS")
    
    # Creating a second symbol (ID 2) to satisfy the circuit breaker foreign key
    symbol_record_infy = make_symbol_row(id=2, ticker="INFY", company_name="Infosys") 
    price_data_record = make_price_data_row(symbols_id=1)
    
    open_circuit_breaker_record = make_open_circuit_breaker_state_table_row(id=1, symbol_id=1)
    closed_circuit_breaker_record = make_open_circuit_breaker_state_table_row(id=2, symbol_id=2, failure_count=0, last_fail_time=None, state=0, cooldown_end_time=None)

    # Inserting baseline data (TCS, INFY)
    cursor.execute("INSERT INTO symbols VALUES(?, ?, ?, ?)", symbol_record_tcs)
    cursor.execute("INSERT INTO symbols VALUES(?, ?, ?, ?)", symbol_record_infy)
    
    # Insert Price data
    cursor.execute("INSERT INTO price_data VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", price_data_record)

    # Insert Circuit Breaker States
    circuit_breaker_states_insertion_sql = "INSERT INTO circuit_breaker_states VALUES (?, ?, ?, ?, ?, ?)"
    circuit_breaker_states_records_to_insert = [open_circuit_breaker_record, closed_circuit_breaker_record]
    cursor.executemany(circuit_breaker_states_insertion_sql, circuit_breaker_states_records_to_insert)
    
    # Commit the permanent, session-long baseline setup
    conn.commit()

    yield conn

    # Teardown - Closing the connection and thus destroy the in-memory db
    conn.close()

# --- 4. MANDATORY FIXTURE: FUNCTION SCOPED TRANSACTIONAL ISOLATION ---

@pytest.fixture(scope="function")
def fresh_db_cursor(in_memory_db: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    """
    CRITICAL FIX: Provides a cursor within a transaction for each test.
    All database modifications (DDL/DML) made by the test are rolled back
    automatically on teardown, ensuring the session-scoped DB remains clean.
    """
    # 1. Get a cursor and explicitly start a transaction
    cursor = in_memory_db.cursor()
    cursor.execute("BEGIN IMMEDIATE")
    
    # 2. Yield the cursor for the test to use
    yield cursor

    # 3. Teardown: Rollback the transaction to revert ALL changes
    in_memory_db.rollback() 
    cursor.close()

# --- 5. DATA ACCESS FIXTURE (Now Safe) ---

@pytest.fixture(scope="function")
def tcs_test_data(fresh_db_cursor: sqlite3.Cursor) -> pd.DataFrame:
    """
    Fetches the seeded TCS data as a clean Pandas DataFrame for a test function.
    It uses the transactional cursor to ensure safety, even though it's read-only.
    """
    query = """
    SELECT timestamp, close 
    FROM price_data 
    WHERE symbols_id = (SELECT id FROM symbols WHERE ticker = 'TCS')
    ORDER BY timestamp
    """
    # Use the connection object from the cursor's context
    df = pd.read_sql(query, fresh_db_cursor.connection, parse_dates=['timestamp'], index_col='timestamp')
    
    # Use the smallest efficient data type (float32) for quant efficiency
    df['close'] = df['close'].astype(np.float32) 
    return df