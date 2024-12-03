from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DataBaseHandler:
    def __init__(self, sqlite_db_path: str):
        """
        Initialize all the context for working with database
        :param sqlite_db_path: path to the sqlite3 database file
        """
        self.engine = create_engine(f'sqlite:///{sqlite_db_path}', echo=False)
        self.connection = self.engine.connect()

    def teardown(self):
        self.connection.close()
