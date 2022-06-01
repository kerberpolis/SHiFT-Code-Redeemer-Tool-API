import pytest

from app import database_controller


@pytest.fixture(scope="session", autouse=True)
def sqlite_connection():
    database = "test_borderlands_codes.db"
    conn = database_controller.create_connection(database)
    database_controller.create_code_table(conn)
    database_controller.create_user_table(conn)
    yield conn
    print("teardown conn")
    conn.close()


@pytest.fixture()
def remove_users(sqlite_connection):
    yield
    cur = sqlite_connection.cursor()
    cur.execute("DELETE FROM users")
    sqlite_connection.commit()
    cur.close()
