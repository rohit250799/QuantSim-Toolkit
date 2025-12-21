from enum import Enum

class LogLevel(Enum):
    """specifies the log level to be stored in the db"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Circuit_State(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF OPEN"

class ValidationIssueType(Enum):
    MISSING_DAY = "MISSING_DAY"
    OUTLIER_5SD = "OUTLIER_5SD"
    STALE_PRICE = "STALE_PRICE"
    UNLANDLED_SPLIT = "UNHANDLED_SPLIT"
    MISSING_VOLUME = "MISSING_VOLUME"

class IssueType(Enum):
    API_RATE_LIMIT = "API Rate Limit"
    API_SERVER_ERROR = "API Server Error"
    NETWORK_TIMEOUT = "Network Timeout"
    VALIDATION_ERROR = "Validation Error"
    CIRCUIT_OPEN = "Circuit Open"
    UNEXPECTED_ERROR = "Unexpected Error"
    API_SUCCESS = "API Success"
    
