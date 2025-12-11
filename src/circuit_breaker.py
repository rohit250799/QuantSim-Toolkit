import logging
import sys
from enum import Enum
from db.database import execute_query

logging.basicConfig(filename='logs/circuit_breaker_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

class Circuit_State(Enum):
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2
class CircuitBreaker:
    def __init__(self) -> None:
        self.default_state_of_circuit_breaker = Circuit_State.CLOSED.value
        self.default_count_of_failures = 0
        self.current_state_of_circuit_breaker = Circuit_State.CLOSED.value

    def get_circuit_state(self, symbol: str) -> int: #returns Open, closed or Half open
        return self.current_state_of_circuit_breaker

    def record_failures(self, symbol: str) -> None:
        pass
        return

    def record_success(self, symbol: str) -> None:
        pass
        return

    def _should_open_circuit(self, symbol: str) -> bool:
        pass
        return False
