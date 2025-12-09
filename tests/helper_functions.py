#"create table if not exists symbols (id integer primary key, ticker text unique not null, " \
#"company_name text, created_at text default CURRENT_TIMESTAMP);"

# price_data_table_creation_query: str = "create table if not exists price_data(id INTEGER PRIMARY KEY, " \
# "symbols_id INTEGER, timestamp TEXT NOT NULL, open REAL,close REAL, high REAL, low REAL, volume int, " \
# "created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(symbols_id, timestamp), FOREIGN KEY (symbols_id) REFERENCES symbols(id));"

# circuit_breaker_states_table_creation_query: str = "create table if not exists circuit_breaker_states(id INTEGER PRIMARY KEY, " \
# "symbol_id INTEGER, failure_count INTEGER, last_fail_time TEXT, state INTEGER NOT NULL, cooldown_end_time TEXT DEFAULT NULL)"

from datetime import datetime, timedelta

current_timestamp = datetime.now().isoformat()
one_day_previous_current_timestamp = (datetime.now() - timedelta(days=1)).isoformat()

#for circuit_breaker_states table row
cooldown_end_time = (datetime.now() + timedelta(hours=1)).isoformat()

def make_symbol_row(id: int = 1, ticker:str = "TCS", company_name: str= "TCS", created_at: str= current_timestamp):
    """A record for the symbols table to test with"""
    return (id, ticker, company_name, created_at)

def make_price_data_row(id: int = 1, symbols_id: str = 1, timestamp: str = one_day_previous_current_timestamp, open: float = 122.43, close: float = 146.81, high: float = 151.04, low: float = 119.63, volume: int = 154, created_at: str = current_timestamp):
    return (id, symbols_id, timestamp, open, close, high, low, volume, created_at)

def make_open_circuit_breaker_state_table_row(id: int = 1, symbol_id: int = 1, failure_count: int = 5, last_fail_time: str = current_timestamp, state: int = 1, cooldown_end_time: str = cooldown_end_time):
    return (id, symbol_id, failure_count, last_fail_time, state, cooldown_end_time)


