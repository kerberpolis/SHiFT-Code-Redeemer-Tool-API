import pytest

from app import database_controller
from app.twitter_streamer import StdOutListener


@pytest.fixture(scope="session", autouse=True)
def sqlite_connection():
    database = "test_borderlands_codes.db"
    conn = database_controller.create_connection(database)
    yield conn
    print("teardown conn")
    conn.close()


@pytest.fixture(scope="function")
def twitter_listener(sqlite_connection):
    return StdOutListener('test.txt', sqlite_connection)
