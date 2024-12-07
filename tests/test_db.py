from sqlalchemy import delete

import pytest

from src.db.database_handler import GammaHandler, Colors


def test_insert_success():
    test_handler = GammaHandler("test_db.sql")
    test_handler.insert([255, 0, 0], 1)
    assert test_handler.select_palette() == {1: (255, 0, 0)}
    query = delete(Colors)
    test_handler.connection.execute(query)
    test_handler.connection.commit()
    test_handler.teardown()


def test_insert_twice():
    test_handler = GammaHandler("test_db.sql")
    test_handler.insert([255, 0, 0], 1)
    test_handler.insert([255, 0, 0], 1)
    assert test_handler.select_palette() == {1: (255, 0, 0)}
    query = delete(Colors)
    test_handler.connection.execute(query)
    test_handler.connection.commit()
    test_handler.teardown()


def test_select_palette():
    test_handler = GammaHandler("test_db.sql")
    test_handler.insert([255, 0, 0], 1)
    test_handler.insert([255, 255, 255], 2)
    test_handler.insert([255, 255, 0], 3)
    assert test_handler.select_palette() == {1: (255, 0, 0), 2: (255, 255, 255), 3: (255, 255, 0)}
    query = delete(Colors)
    test_handler.connection.execute(query)
    test_handler.connection.commit()
    test_handler.teardown()


def test_get_rgb():
    test_handler = GammaHandler("test_db.sql")
    test_handler.insert([255, 0, 0], 1)
    test_handler.insert([255, 255, 255], 2)
    test_handler.insert([255, 255, 0], 3)
    assert test_handler.get_rgb(1) == (255, 0, 0)
    assert test_handler.get_rgb(2) == (255, 255, 255)
    assert test_handler.get_rgb(3) == (255, 255, 0)
    query = delete(Colors)
    test_handler.connection.execute(query)
    test_handler.connection.commit()
    test_handler.teardown()


def test_get_rgb_non_existing():
    test_handler = GammaHandler("test_db.sql")
    test_handler.insert([255, 0, 0], 1)
    with pytest.raises(ValueError, match="Non-existing Gamma code: -1"):
        test_handler.get_rgb(-1)
    query = delete(Colors)
    test_handler.connection.execute(query)
    test_handler.connection.commit()
    test_handler.teardown()
