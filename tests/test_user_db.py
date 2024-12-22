from sqlalchemy import select, delete

from src.db.user_database_handler import UserDatabaseHandler, UserIdTable, UserAvailableTable, UserSettingsTable


def test_clear_db():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    test_handler.connection.execute(delete(UserIdTable))
    test_handler.connection.execute(delete(UserAvailableTable))
    test_handler.connection.execute(delete(UserSettingsTable))
    test_handler.connection.commit()
    test_handler.teardown()


def test_insert_success():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    test_handler.insert_user(42)
    assert test_handler.get_user_id(42) == 1
    test_handler.teardown()


def test_insert_twice():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    test_handler.insert_user(42)
    test_handler.insert_user(42)
    query = select(UserIdTable)
    result = test_handler.connection.execute(query).fetchall()
    assert len(result) == 1
    test_handler.teardown()


def test_insert_available():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    test_handler.insert_available(42, 101, 1)
    query = select(UserAvailableTable).where(UserAvailableTable.UserId == test_handler.get_user_id(42))
    result = test_handler.connection.execute(query).fetchone()
    assert list(result[2:]) == [101, 1]
    test_handler.teardown()

def test_select_available():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    test_handler.insert_available(42, 101, 1)
    test_handler.insert_available(42, 102, 3)
    result = test_handler.select_available_colors(42)
    assert len(result) == 2
    assert (101, 1) in result
    assert (102, 3) in result

def test_update_user_settings():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    settings = test_handler.get_user_settings(42)
    assert settings == 0
    test_handler.update_user_settings(42, 13)
    settings = test_handler.get_user_settings(42)
    assert settings == 13

def test_update_user_settings_incorrect():
    test_handler = UserDatabaseHandler("test_user_db.sql")
    try:
        test_handler.update_user_settings(42, 15)
        assert False
    except ValueError as e:
        assert str(e) == "Settings must be between 0 and 14"