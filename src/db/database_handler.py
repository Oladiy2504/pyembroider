from sqlalchemy import Column, Integer, UniqueConstraint, create_engine, insert
from sqlalchemy.exc import IntegrityError
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


class Colors(Base):
    __tablename__ = "colors"

    ColorId = Column(Integer, primary_key=True)
    Gamma = Column(Integer)
    R = Column(Integer)
    G = Column(Integer)
    B = Column(Integer)

    __table_args__ = (
        UniqueConstraint('Gamma', 'R', 'G', 'B', name='uix_colors'),
    )


class GammaHandler(DataBaseHandler):
    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)
        Base.metadata.create_all(self.engine)

    def insert(self, rgb: list[int], gamma_code: int) -> None:
        """
        Insert a new gamma-color into the database
        :param rgb: list of rgb values
        :param gamma_code: code in Gamma system
        :return: nothing
        """
        try:
            query = insert(Colors).values(Gamma=gamma_code, R=rgb[0], G=rgb[1], B=rgb[2])
            self.connection.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass
