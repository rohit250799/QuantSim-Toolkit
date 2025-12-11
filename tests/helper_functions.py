from datetime import datetime, timedelta
from typing import Tuple

current_timestamp = datetime.now().isoformat()
one_day_previous_current_timestamp = (datetime.now() - timedelta(days=1)).isoformat()

#for circuit_breaker_states table row
cooldown_end_time = (datetime.now() + timedelta(hours=1)).isoformat()

def make_symbol_row(id: int = 1, ticker:str = "TCS", company_name: str= "TCS", created_at: str= current_timestamp) -> Tuple[int, str, str, str]:
    """A record for the symbols table to test with"""
    return (id, ticker, company_name, created_at)

def make_price_data_row(id: int = 1, symbols_id: int = 1, timestamp: str = one_day_previous_current_timestamp, open: float = 122.43, close: float = 146.81, high: float = 151.04, low: float = 119.63, volume: int = 154, created_at: str = current_timestamp) -> Tuple[int, int, str, float, float, float, float, int, str]:
    return (id, symbols_id, timestamp, open, close, high, low, volume, created_at)

def make_open_circuit_breaker_state_table_row(id: int = 1, symbol_id: int = 1, failure_count: int = 5, last_fail_time: str | None = current_timestamp, state: int = 1, cooldown_end_time: str | None = cooldown_end_time) -> Tuple[int, int, int, str | None, int | None, str | None]:
    return (id, symbol_id, failure_count, last_fail_time, state, cooldown_end_time)

def can_call_api(state: int) -> bool:
    return state in (0, 2)


