from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Circuit_State(Enum):
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2

class ValidationIssueType(Enum):
    MISSING_DAY = "MISSING_DAY"
    OUTLIER_5SD = "OUTLIER_5SD"
    STALE_PRICE = "STALE_PRICE"
    UNLANDLED_SPLIT = "UNHANDLED_SPLIT"
    MISSING_VOLUME = "MISSING_VOLUME"


