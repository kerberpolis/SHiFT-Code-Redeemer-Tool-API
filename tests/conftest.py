import pytest

from app import database_controller


@pytest.fixture(scope="session", autouse=True)
def sqlite_connection():
    database = "./tests/files/test_borderlands_codes.db"
    conn = database_controller.create_connection(database)
    database_controller.create_code_table(conn)
    database_controller.create_user_table(conn)
    yield conn
    conn.close()


@pytest.fixture()
def remove_users(sqlite_connection):
    yield
    cur = sqlite_connection.cursor()
    cur.execute("DELETE FROM users")
    sqlite_connection.commit()
    cur.close()


@pytest.fixture()
def seed_users_table(sqlite_connection):
    users = [
        {
            'gearbox_email': 'test_email_1',
            'gearbox_password': 'test_password_1',
        },
        {
            'gearbox_email': 'test_email_2',
            'gearbox_password': 'test_password_2',
        }

    ]

    for user in users:
        database_controller.create_user(sqlite_connection, user)

    yield
