import pytest
from starlette.testclient import TestClient
from app import main
from app import database_controller
from app.util import generate_uuid


@pytest.fixture(scope="function")
def test_client():
    app = main.get_app()
    yield TestClient(app)


@pytest.fixture(scope="function")
def sqlite_connection():
    database = "./tests/files/test_borderlands_codes.db"
    conn = database_controller.create_connection(database)
    database_controller.create_code_table(conn)
    database_controller.create_user_table(conn)
    database_controller.create_user_code_table(conn)
    seed_tables(conn)
    yield conn
    teardown(conn)
    conn.close()


def teardown(sqlite_connection):
    cur = sqlite_connection.cursor()
    cur.execute("DELETE FROM user")
    cur.execute("DELETE FROM code")
    cur.execute("DELETE FROM user_code")
    sqlite_connection.commit()
    cur.close()


def seed_tables(sqlite_connection):
    users = [
        {
            'uuid': generate_uuid(),
            'email': 'test_email_1',
            'password': 'test_password_1',
            'gearbox_email': 'test_gearbox_email_1',
            'gearbox_password': 'test_gearbox_password_1',
        },
        {
            'uuid': generate_uuid(),
            'email': 'test_email_2',
            'password': 'test_password_2',
            'gearbox_email': 'test_gearbox_email_2',
            'gearbox_password': 'test_gearbox_password_2',
        },
        {
            'uuid': generate_uuid(),
            'email': 'test_email_3',
            'password': 'test_password_3',
            'gearbox_email': 'test_gearbox_email_3',
            'gearbox_password': 'test_gearbox_password_3',
        }
    ]
    for user in users:
        database_controller.create_user(sqlite_connection, user)

    codes = [
        {
            'game': 'Borderlands 3', 'platform': 'Universal', 'code': '3BRTJ-5K659-K5355-BTB3T-633F3',
            'type': 'shift', 'reward': '1 GOLD KEY', 'time_gathered': 'Unknown',
            'expires': 'Unknown'
        },
        {
            'game': 'Borderlands 3', 'platform': 'Universal', 'code': 'KSWJJ-J6TTJ-FRCF9-X333J-5Z6KJ',
            'type': 'shift', 'reward': '3 GOLD KEY', 'time_gathered': 'Unknown',
            'expires': 'Unknown'
        },
        {
            'game': 'WONDERLANDS', 'platform': 'Universal', 'code': 'TBRJJ-TW659-W5B5C-T3B3J-3BTBK',
            'type': 'shift', 'reward': '10 SKELETON KEYS', 'time_gathered': 'Unknown',
            'expires': 'Unknown'
        },
        {
            'game': 'WONDERLANDS', 'platform': 'Universal', 'code': 'KSK33-S5T33-XX5FS-R3BTB-WSXRC',
            'type': 'shift', 'reward': '1 SKELETON KEYS', 'time_gathered': 'Unknown',
            'expires': 'Unknown'
        },
        {
            'game': 'Borderlands 3', 'platform': 'Universal', 'code': 'W9CJT-5XJTB-RRKRS-FTJ3T-BTRKK',
            'type': 'shift', 'reward': 'Trinket or something', 'time_gathered': 'Unknown',
            'expires': 'Unknown'
        }
    ]
    for code in codes:
        database_controller.create_code(sqlite_connection, code)
