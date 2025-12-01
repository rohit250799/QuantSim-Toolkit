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