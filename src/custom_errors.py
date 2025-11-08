class RecordNotFoundError(Exception):
    """Exception raised for when records are not found in the db"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"