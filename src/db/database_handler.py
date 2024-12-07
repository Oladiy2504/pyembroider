from sqlalchemy import Column, Integer, UniqueConstraint, create_engine, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base

ColorBase = declarative_base()


class DataBaseHandler:
    """
    Base class for database handlers.
    """

    def __init__(self, sqlite_db_path: str):
        """
        Initialize all the context for working with database
        :param sqlite_db_path: path to the sqlite3 database file
        """
        self.engine = create_engine(f'sqlite:///{sqlite_db_path}', echo=False)
        self.connection = self.engine.connect()

    def teardown(self):
        self.connection.close()


class Colors(ColorBase):
    """
    Class for table with Gamma-colors
    """
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
    """
    Handler for Gamma-colors database
    """
    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)
        ColorBase.metadata.create_all(self.engine)

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

    def select_palette(self) -> dict[int: tuple[int, int, int]]:
        """
        Select all Gamma palette
        :return: dict of format {gamma_code: (r, g, b)}
        """
        query = select(Colors)
        results = self.connection.execute(query).fetchall()
        return {idx: (r, g, b) for i, idx, r, g, b in results}

    def get_rgb(self, gamma_id: int) -> tuple[int, int, int]:
        """
        Get rgb from gamma_id
        :param gamma_id: id in Gamma system
        :return: tuple (r, g, b)
        """
        query = select(Colors.R, Colors.G, Colors.B).where(Colors.Gamma == gamma_id)
        results = self.connection.execute(query).fetchall()
        if len(results) == 0:
            raise ValueError(f"Non-existing Gamma code: {gamma_id}")
        return results[0]
