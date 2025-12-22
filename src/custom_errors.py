from typing import Optional

class RecordNotFoundError(Exception):
    """Exception raised for when records are not found in the db"""

    def __init__(self, message: Optional[str]) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"
    
class RecordInsertionError(Exception):
    """Exception raised when the record is not properly inserted in the db"""

    def __init__(self, message: Optional[str]) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"
    
class TableDoesNotExistError(Exception):
    """Exception raised when a the specific table does not exist in the db"""

    def __init__(self, message: Optional[str]) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"
    
class CircuitOpenStateError(Exception):
    """Exceotion raised when the current state of a circuit is Open, so no API calls allowed"""

    def __init__(self, message: Optional[str]) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"
    
