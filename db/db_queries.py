price_data_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS price_data (
    ticker TEXT NOT NULL,
    timestamp INTEGER NOT NULL, 
    open REAL,
    close REAL, 
    high REAL, 
    low REAL,
    volume INTEGER,
    PRIMARY KEY (ticker, timestamp)
)
"""

symbol_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS symbols (
    ticker TEXT NOT NULL PRIMARY KEY, 
    company_name TEXT,
    exchange TEXT,
    sector TEXT, 
    currency TEXT 
    created_at INTEGER NOT NULL
    )
"""

circuit_breaker_states_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS circuit_breaker_states(
    ticker TEXT NOT NULL PRIMARY KEY,
    state TEXT NOT NULL,
    failure_count INTEGER NOT NULL DEFAULT 0, 
    last_fail_time INTEGER, 
    cooldown_end_time INTEGER 
)
"""

system_logs_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    level TEXT NOT NULL,
    source TEXT,
    message TEXT NOT NULL,
    ticker TEXT,
    api_status_code INTEGER,
    response_time_ms REAL
)
"""

validation_log_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS validation_log (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date INTEGER NOT NULL,
    issue_type TEXT NOT NULL,
    description TEXT,
    resolved INTEGER NOT NULL DEFAULT 0
)
"""

system_config_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT, 
    description TEXT 
)
"""

list_all_existing_tables_query: str = """
SELECT name FROM sqlite_schema WHERE type = 'table'
AND name NOT LIKE 'sqlite_%'
"""

record_circuit_state_initialization_query: str = """
INSERT OR IGNORE INTO circuit_breaker_states VALUES (
    ?, ?, ?, ?, ?
)
"""

set_circuit_state_query: str = """
UPDATE circuit_breaker_states
SET state = ?, failure_count = ?, last_fail_time = ?, cooldown_time = ?
WHERE ticker = ?
"""

get_historical_data_query: str = """
SELECT * FROM price_data where ticker = ? and timestamp between ? AND ? ORDER BY timestamp ASC
"""

insert_or_update_record_in_symbols_table_query: str = """
INSERT INTO symbols VALUES (?, ?, ?, ?, ?, ?)
"""

get_all_entries_of_ticker_from_validation_log_table_query: str = """
SELECT * FROM validation_log where ticker = ? ORDER BY date ASC
"""

insert_triggered_indices_in_validation_log_query: str = """
INSERT INTO validation_log (ticker, date, issue_type, description) values (?, ?, ?, ?)
"""

delete_validation_log: str = """
DELETE FROM validation_log WHERE ticker = ? AND resolved = 0
"""

system_logs_insertion_query: str = """
INSERT INTO system_logs (timestamp, level, source, message, ticker, api_status_code, response_time_ms) 
VALUES (?, ?, ?, ?, ?, ?, ?) 
"""

analysis_results_table_creation_query: str = """
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    benchmark TEXT NOT NULL,
    start_date INT,
    end_date INT,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL, 
    volatility REAL,
    correlation REAL,
    data_quality_score REAL
)
"""

insert_record_into_analysis_results_table: str = """
INSERT INTO analysis_results (timestamp, ticker, benchmark, start_date, end_date, alpha, beta, sharpe_ratio, ticker_volatility, benchmark_volatility, correlation, data_quality_score)
values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

rename_volatility_to_ticker_volatility_in_analysis_results_query: str = """
ALTER TABLE analysis_results RENAME COLUMN volatility to ticker_volatility 
"""

add_new_column_benchmark_volatility_in_analysis_results_query: str = """
ALTER TABLE analysis_results ADD COLUMN benchmark_volatility REAL
"""

check_if_ticker_exists_in_price_data: str = """
SELECT 1 FROM price_data WHERE ticker = ? LIMIT 1
"""

index_creation_for_price_data_table: str = """
CREATE INDEX IF NOT EXISTS idx_price_data_ticker_timestamp ON price_data (ticker, timestamp)
"""