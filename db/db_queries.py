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
    is_open TEXT NOT NULL,
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