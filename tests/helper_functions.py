from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple
from src.quant_enums import Circuit_State



#current_timestamp = datetime.now().isoformat()
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

def make_open_circuit_breaker_state_table_row(ticker: str = 'TCS', state: str = Circuit_State.OPEN.value, failure_count: int = 5, last_fail_time: int = unix_timestamp_value, cooldown_end_time: int = cooldown_end_time_unix) -> Tuple[str, str, int, int, int]:
    """A record for open circuit state to test with"""
    return (ticker, state, failure_count, last_fail_time, cooldown_end_time)

def make_closed_circuit_breaker_state_table_row(ticker: str = 'INFY', state: str = Circuit_State.CLOSED.value, failure_count: int = 0, last_fail_time: int | None = None, cooldown_end_time: int | None = None) -> Tuple[str, str, int, int | None, int | None]:
    """A record for open circuit state to test with"""
    return (ticker, state, failure_count, last_fail_time, cooldown_end_time)

def can_call_api(state: str) -> bool:
    """
    Returns a boolean value which represents if the API can be called. True represents the API can be called and False represents it cannot be called
    """
    return state in ('CLOSED', 'HALF_OPEN')