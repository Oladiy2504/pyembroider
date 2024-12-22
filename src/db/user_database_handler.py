from sqlalchemy import Column, Integer, UniqueConstraint, insert, select, update, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship

from src.db.database_handler import DataBaseHandler

UserBase = declarative_base()


class UserIdTable(UserBase):
    """
    Class for table with tg_user_ids
    """
    __tablename__ = "user_id"

    Id = Column(Integer, primary_key=True)
    TgUserId = Column(Integer)

    settings = relationship("UserSettingsTable", back_populates="user_id")
    available = relationship("UserAvailableTable", back_populates="user_id")

    __table_args__ = (
        UniqueConstraint('TgUserId', name='tg_id'),
    )


class UserSettingsTable(UserBase):
    """
    Class for table with user settings
    """
    __tablename__ = "user_settings"

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('user_id.Id'))
    UserSettings = Column(Integer, default=0)

    user_id = relationship("UserIdTable", back_populates="settings")

    __table_args__ = (
        UniqueConstraint('UserId', name='user_id'),
    )


class UserAvailableTable(UserBase):
    """
    Class for table with string colors, available for all users
    """
    __tablename__ = "user_available"

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('user_id.Id'))
    GammaId = Column(Integer)
    Count = Column(Integer)

    user_id = relationship("UserIdTable", back_populates="available")

    __table_args__ = (
        UniqueConstraint('UserId', 'GammaId', name='user_color_pair'),
    )


class UserDatabaseHandler(DataBaseHandler):
    """
    Handler for user database.
    """

    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)
        UserBase.metadata.create_all(self.engine)

    def insert_user(self, tg_id):
        try:
            query = insert(UserIdTable).values(TgUserId=tg_id)
            self.connection.execute(query)
            self.connection.commit()
            user_id = self.get_user_id(tg_id)
            query = insert(UserSettingsTable).values(UserId=user_id)
            self.connection.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass

    def get_user_id(self, tg_id: int) -> int:
        """
        Insert a new line into user available colors database
        :param tg_id: telegram user id
        :return: user id from UserIdTable
        """
        query = select(UserIdTable.Id).where(UserIdTable.TgUserId == tg_id)
        results = self.connection.execute(query).fetchone()
        return results[0]


    def insert_available(self, tg_id: int, gamma_id: int, count: int) -> None:
        """
        Insert a new line into user available colors database
        :param tg_id: id of telegram user
        :param gamma_id: id of a color in Gamma table
        :param count: list of rgb values
        :return: nothing
        """
        try:
            user_id = self.get_user_id(tg_id)
            query = insert(UserAvailableTable).values(UserId=user_id, GammaId=gamma_id, Count=count)
            self.connection.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass

    def select_available_colors(self, tg_id: int) -> list[tuple[int, int]]:
        """
        Selects all the available colors in user database
        :return: list of available colors gamma_ids with counts
        """
        query = select(UserAvailableTable.GammaId, UserAvailableTable.Count).join(UserIdTable).where(UserIdTable.TgUserId == tg_id)
        results = self.connection.execute(query).fetchall()
        return results

    def update_user_settings(self, tg_id: int, settings: int) -> None:
        if settings < 0 or settings > 14:
            raise ValueError("Settings must be between 0 and 14")
        user_id = self.get_user_id(tg_id)
        query = update(UserSettingsTable).where(UserSettingsTable.UserId == user_id).values(UserSettings=settings)
        self.connection.execute(query)
        self.connection.commit()

    def get_user_settings(self, tg_id: int) -> int:
        user_id = self.get_user_id(tg_id)
        query = select(UserSettingsTable.UserSettings).where(UserSettingsTable.UserId == user_id)
        result = self.connection.execute(query).fetchone()
        return result[0]

