from sqlite3 import Connection

from db.database import get_prod_conn

class DataLoader:
    """
    Provides all methods necessary to abstract all DB I/O operations, schema management(migrations)
    and data formatting(like date conversion)

    Must: hold the active SQLite connection and cursor as attributes
    """
    def __init__(self, db_conn: None | Connection = None) -> None:
        self.prod_db_connection = db_conn if db_conn is not None else get_prod_conn()
        self._run_migrations()
        pass

    # def _get_db_connection(self):
    #     """
    #     Executes the entire migration sequence (DROP then CREATE) as a single Atomic Transaction(Commit/Rollback on failure)
    #     """
    #     conn = self.prod_db_connection

    #     pass


    def _run_migrations(self):
        """Handles one-time cleanup and schema creation"""
        
        pass


