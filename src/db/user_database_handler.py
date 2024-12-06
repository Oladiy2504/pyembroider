from sqlalchemy import Column, Integer, UniqueConstraint, create_engine, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base

UserBase = declarative_base()


class UserDataBaseHandler:
    def __init__(self, sqlite_db_path: str):
        """
        Initialize all the context for working with database
        :param sqlite_db_path: path to the sqlite3 database file
        """
        self.engine = create_engine(f'sqlite:///{sqlite_db_path}', echo=False)
        self.connection = self.engine.connect()

class UserColors(UserBase):
    __tablename__ = "user_colors"

    ColorId = Column(Integer, primary_key=True)
    Gamma = Column(Integer)
    R = Column(Integer)
    G = Column(Integer)
    B = Column(Integer)

    __table_args__ = (
        UniqueConstraint('Gamma', 'R', 'G', 'B', name='uix_colors'),
    )


class UserGammaHandler(UserDataBaseHandler):
    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)
        UserBase.metadata.create_all(self.engine)

    def insert(self, rgb: list[int], gamma_code: int) -> None:
        """
        Insert a new gamma-color into the user database
        :param rgb: list of rgb values
        :param gamma_code: code in Gamma system
        :return: nothing
        """
        try:
            query = insert(UserColors).values(Gamma=gamma_code, R=rgb[0], G=rgb[1], B=rgb[2])
            self.connection.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass
        

