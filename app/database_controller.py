import logging
import os
import sqlite3
from sqlite3 import Error, Connection

from cryptography.fernet import Fernet

from app.config import GEARBOX_EMAIL, GEARBOX_PASSWORD


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Error as e:
        print(e)

    return conn


def create_user_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS users(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                gearbox_email TEXT NOT NULL UNIQUE,
                gearbox_password TEXT NOT NULL UNIQUE
            )"""

    create_table(conn, sql)


def create_code_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS codes(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                game TEXT,
                platform TEXT,
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                reward TEXT DEFAULT Unknown,
                time_gathered TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires TEXT,
                attempts INT NOT NULL DEFAULT 0,
                valid INT NOT NULL DEFAULT 0,
                UNIQUE(game, code, type)
                UNIQUE(code, type)
            )"""

    create_table(conn, sql)


def create_table(conn: Connection, sql: str):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
        logging.debug(e)


def create_code(conn: Connection, code_data: dict):
    """
    Create a new code into the codes table.
    """
    cur = None

    sql = '''INSERT INTO codes(game, platform, code, type, reward, time_gathered, expires)
             VALUES(:game, :platform, :code, :type, :reward, :time_gathered, :expires)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, code_data)
        conn.commit()
        logging.info(f'Creating {code_data["game"]} code {code_data["code"]} in database table codes')
    except sqlite3.IntegrityError as e:
        # logging.debug(f'Code data {code_data} already exists. Error: {str(e)}')  # cannot add due to unique constraints
        pass
    except sqlite3.DatabaseError as e:
        logging.debug(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        logging.debug(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def update_invalid_code(conn: Connection, code_id: int):
    """
    update the validity of the code
    """
    sql = '''UPDATE codes
             SET valid = 1
             WHERE _id = ?'''

    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id, ))
    cur.close()


def update_valid_code(conn: Connection, code_id: int):
    """
    update the validity of the code
    """
    sql = '''UPDATE codes
             SET valid = 0
             WHERE _id = ?'''

    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id, ))
    cur.close()
    logging.info(f'Code {code_id} has been set to invalid')


def delete_code(conn: Connection, code_id: int):
    """
    Delete a code by code id
    """
    sql = 'DELETE FROM codes WHERE _id=?'
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id,))
    cur.close()


def delete_all_codes(conn: Connection):
    """
    Delete all rows in the codes table
    """
    sql = 'DELETE FROM codes'
    cur = conn.cursor()
    with conn:
        cur.execute(sql)
    cur.close()


def select_all_codes(conn: Connection):
    """
    Query all rows in the codes table
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM codes")
    rows = cur.fetchall()

    return rows


def select_valid_codes(conn: Connection):
    """
    Query codes by validity
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM codes WHERE valid=0")
    rows = cur.fetchall()

    cur.close()

    return rows


def select_codes_by_id(conn: Connection, code_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM codes WHERE _id=?", (code_id, ))
    rows = cur.fetchall()

    return rows


def increment_attempts(conn: Connection, code_id: int):
    """
    Update attempts attribute by 1
    """
    sql = '''UPDATE codes
             SET attempts = attempts + 1
             WHERE _id = ?'''
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id, ))
    cur.close()


def get_attempts(conn: Connection, code_id):
    """
    Query code attempts by id
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT attempts FROM codes WHERE _id=?", (code_id, ))
    attempts = cur.fetchone()

    return attempts[0]


def create_user(conn: Connection, user_data: dict):
    sql = '''INSERT INTO users(gearbox_email, gearbox_password)
                 VALUES(:gearbox_email, :gearbox_password)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, user_data)
        conn.commit()
        print(f'Creating User {user_data["gearbox_email"]} in database table users')
    except sqlite3.IntegrityError as e:
        print(f'User could not be created due to Integrity issue. Error: {str(e)}')
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def select_all_users(conn: Connection):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()


def select_user_by_gearbox_email(conn: Connection, gearbox_email: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE gearbox_email=?", (gearbox_email, ))
    return cur.fetchone()


def select_user_by_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE _id=?", (user_id, ))
    return cur.fetchone()


def remove_user_by_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE _id=?", (user_id, ))
    conn.commit()
    cur.close()


def encrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


if __name__ == "__main__":
    database = "borderlands_codes.db"
    db_conn = create_connection(database)

    key = os.getenv('BORDERLANDS_USER_CRYPTOGRAPHY_KEY')
    user = select_user_by_gearbox_email(db_conn, GEARBOX_EMAIL)

    if user is None:
        if key:
            if GEARBOX_EMAIL and GEARBOX_PASSWORD:
                token = encrypt(GEARBOX_PASSWORD.encode(), key.encode())

                my_data = {
                    'gearbox_email': GEARBOX_EMAIL,
                    'gearbox_password': token,
                }
                rowid = create_user(db_conn, my_data)
                print(rowid)
                user = select_user_by_gearbox_email(db_conn, GEARBOX_EMAIL)
                print(user)
        else:
            print('Must have environment variable `BORDERLANDS_USER_CRYPTOGRAPHY_KEY` set.')

    print(user)
    msg = decrypt(user[2], key.encode())
    print(msg.decode())

