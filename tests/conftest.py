import pytest
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Generator, Any, Tuple
from db.database import execute_query

from src.quant_enums import Circuit_State

# --- 1. MOCKING DEPENDENCIES ---
# Define the mock data helper functions here or ensure they are imported.
timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
unix_timestamp_value = int(timestamp.timestamp())
one_day_previous_current_timestamp = (datetime.now() - timedelta(days=1)).isoformat()

#for circuit_breaker_states table row
cooldown_end_time = (datetime.now() + timedelta(hours=1))
cooldown_end_time_unix = int(cooldown_end_time.timestamp())

def make_symbol_row(ticker:str = "TCS", company_name: str= "TCS", exchange: str = 'BSE', sector: str = 'Tech', currency: str = 'INR', created_at: int= 1766302200) -> Tuple[str, str, str, str, str, int]:
    """A record for the symbols table to test with"""
    return (ticker, company_name, exchange, sector, currency, created_at)

def make_price_data_row(ticker: str = 'TCS', timestamp: int = unix_timestamp_value, open: float = 122.43, close: float = 146.81, high: float = 151.04, low: float = 119.63, volume: int = 154) -> Tuple[str, int, float, float, float, float, int]:
    """A record for price_data table to test with"""
    return (ticker, timestamp, open, close, high, low, volume)

def make_open_circuit_breaker_state_table_row(ticker: str = 'TCS', state: Circuit_State = Circuit_State.OPEN.value, failure_count: int = 5, last_fail_time: int = unix_timestamp_value, cooldown_end_time: int = cooldown_end_time_unix):
    """A record for open circuit state to test with"""
    return (ticker, state, failure_count, last_fail_time, cooldown_end_time)

def make_closed_circuit_breaker_state_table_row(ticker: str = 'INFY', state: Circuit_State = Circuit_State.CLOSED.value, failure_count: int = 0, last_fail_time: int | None = None, cooldown_end_time: int | None = None):
    """A record for open circuit state to test with"""
    return (ticker, state, failure_count, last_fail_time, cooldown_end_time)

# --- 2. DATABASE SCHEMA DEFINITION (DDL) ---
DB_SCHEMA_DDL = """
-- table to store the price data results
CREATE TABLE IF NOT EXISTS price_data (
    ticker TEXT NOT NULL,
    timestamp INTEGER NOT NULL, 
    open REAL,
    close REAL, 
    high REAL, 
    low REAL,
    volume INTEGER,
    PRIMARY KEY (ticker, timestamp)
);

CREATE TABLE IF NOT EXISTS symbols (
    ticker TEXT NOT NULL PRIMARY KEY, 
    company_name TEXT,
    exchange TEXT,
    sector TEXT, 
    currency TEXT, 
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS circuit_breaker_states(
    ticker TEXT NOT NULL PRIMARY KEY,
    state TEXT NOT NULL,
    failure_count INTEGER NOT NULL DEFAULT 0, 
    last_fail_time INTEGER, 
    cooldown_end_time INTEGER 
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    level TEXT NOT NULL,
    source TEXT,
    message TEXT NOT NULL,
    ticker TEXT,
    api_status_code INTEGER,
    response_time_ms REAL
);

CREATE TABLE IF NOT EXISTS validation_log (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date INTEGER NOT NULL,
    issue_type TEXT NOT NULL,
    description TEXT,
    resolved INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT, 
    description TEXT 
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
    symbol_record_tcs = make_symbol_row()
    symbol_record_infy = make_symbol_row(ticker="INFY", company_name="Infosys", exchange="BSE", sector="Tech", currency="INR", created_at=1766302100) 

    price_data_record = make_price_data_row()

    open_circuit_breaker_record = make_open_circuit_breaker_state_table_row()
    closed_circuit_breaker_record = make_closed_circuit_breaker_state_table_row()
    
    # Inserting baseline data (TCS, INFY)
    cursor.execute("INSERT INTO symbols(ticker, company_name, exchange, sector, currency, created_at) VALUES(?, ?, ?, ?, ?, ?)", symbol_record_tcs)
    cursor.execute("INSERT INTO symbols(ticker, company_name, exchange, sector, currency, created_at) VALUES(?, ?, ?, ?, ?, ?)", symbol_record_infy)
    
    # Insert Price data
    cursor.execute("INSERT INTO price_data(ticker, timestamp, open, close, high, low, volume) VALUES(?, ?, ?, ?, ?, ?, ?)", price_data_record)

    # Insert Circuit Breaker States
    circuit_breaker_states_insertion_sql = "INSERT INTO circuit_breaker_states(ticker, state, failure_count, last_fail_time, cooldown_end_time) VALUES (?, ?, ?, ?, ?)"
    circuit_breaker_states_records_to_insert = [open_circuit_breaker_record, closed_circuit_breaker_record]
    cursor.executemany(circuit_breaker_states_insertion_sql, circuit_breaker_states_records_to_insert)
    
    # Committing the permanent, session-long baseline setup
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
    
    # Using the smallest efficient data type (float32) for quant efficiency
    df['close'] = df['close'].astype(np.float32) 
    return df

def fetch_scalar(conn, query, params):
    """A helper function to fetch specific data from the db table"""
    rows = execute_query(conn, query, params)
    if len(rows) != 1:
        raise ValueError(f"Expected 1 row, got {len(rows)}")
    return rows[0][0]


