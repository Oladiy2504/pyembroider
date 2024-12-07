from sqlalchemy import Column, Integer, UniqueConstraint, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base

from src.db.database_handler import DataBaseHandler

UserBase = declarative_base()


class UserAvailableTable(UserBase):
    """
    Class for table with string colors, available for user
    """
    __tablename__ = "user_available"

    Id = Column(Integer, primary_key=True)
    GammaId = Column(Integer)
    Count = Column(Integer)

    __table_args__ = (
        UniqueConstraint('GammaId', name='uix_colors'),
    )


class UserAvailableHandler(DataBaseHandler):
    """
    Handler for user database.
    """

    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)
        UserBase.metadata.create_all(self.engine)

    def insert(self, gamma_id: int, count: int) -> None:
        """
        Insert a new line into user database
        :param gamma_id: id of a color in Gamma table
        :param count: list of rgb values
        :return: nothing
        """
        try:
            query = insert(UserAvailableTable).values(GammaId=gamma_id, Count=count)
            self.connection.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass

    def select_colors(self) -> dict[int: tuple[int, int, int]]:
        """
        Selects all the available colors in user database
        :return: list of available colors gamma_ids
        """
        query = select(UserAvailableTable.GammaId)
        results = self.connection.execute(query).fetchall()
        return [i[0] for i in results]
