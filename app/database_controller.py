import sqlite3
from sqlite3 import Error
import logging
from app.config import GEARBOX_EMAIL, GEARBOX_PASSWORD
import bcrypt


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Error as e:
        print(e)

    return conn


def create_user_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS users(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                gearbox_email TEXT NOT NULL UNIQUE,
                gearbox_password TEXT NOT NULL UNIQUE,
                salt TEXT NOT NULL
            )"""

    create_table(conn, sql)


def create_code_table(conn):
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


def create_table(conn, sql):
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


def create_code(conn, code_data):
    """
    Create a new project into the codes table
    :param code_data:
    """
    cur = None

    sql = '''INSERT INTO codes(game, platform, code, type, reward, time_gathered, expires)
             VALUES(:game, :platform, :code, :type, :reward, :time_gathered, :expires)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, code_data)
        conn.commit()
        print(f'Creating {code_data[0]} code {code_data[2]} in database table codes')
    except sqlite3.IntegrityError as e:
        # print(f'Code data {code_data} already exists. Error: {str(e)}')  # cannot add due to unique constraints
        pass
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def update_invalid_code(conn, id):
    """
    update the validity of the code
    :param id: id of the code
    """
    sql = '''UPDATE codes
             SET valid = 1
             WHERE _id = ?'''

    cur = conn.cursor()
    with conn:
        cur.execute(sql, (id, ))
    cur.close()


def update_valid_code(conn, id):
    """
    update the validity of the code
    :param id: id of the code
    """
    sql = '''UPDATE codes
             SET valid = 0
             WHERE _id = ?'''

    cur = conn.cursor()
    with conn:
        cur.execute(sql, (id, ))
    cur.close()
    logging.info(f'Code {id} has been set to invalid')


def delete_code(conn, id):
    """
    Delete a code by code id
    :param id: id of the code
    :return:
    """
    sql = 'DELETE FROM codes WHERE _id=?'
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (id,))
    cur.close()


def delete_all_codes(conn):
    """
    Delete all rows in the codes table
    """
    sql = 'DELETE FROM codes'
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (id,))
    cur.close()


def select_all_codes(conn):
    """
    Query all rows in the codes table
    :return:
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM codes")
    rows = cur.fetchall()

    return rows


def select_valid_codes(conn):
    """
    Query codes by validity
    :return:
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM codes WHERE valid=0")
    rows = cur.fetchall()

    cur.close()

    return rows


def select_codes_by_type(conn, type):
    """
    Query codes by type
    :param type: the type of code
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM codes WHERE type=?", (type, ))
    rows = cur.fetchall()

    return rows


def select_codes_by_id(conn, id):
    """
    Query codes by type
    :param type: the type of code
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM codes WHERE _id=?", (id, ))
    rows = cur.fetchall()

    return rows


def increment_attempts(conn, id):
    """
    Update attempts attribute by 1
    """
    sql = '''UPDATE codes
             SET attempts = attempts + 1
             WHERE _id = ?'''
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (id, ))
    cur.close()


def get_attempts(conn, id):
    """
    Query code attempts by id
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT attempts FROM codes WHERE _id=?", (id, ))
    attempts = cur.fetchone()

    return attempts[0]


def create_user(conn, user_data):
    sql = '''INSERT INTO users(gearbox_email, gearbox_password, salt)
                 VALUES(:gearbox_email, :gearbox_password, :salt)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, user_data)
        conn.commit()
        print(f'Creating User {user_data[0]} in database table users')
    except sqlite3.IntegrityError as e:
        print(f'User could not be created due to Integrity issue. Error: {str(e)}')
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def select_all_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()


def select_user_by_gearbox_email(conn, gearbox_email):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE gearbox_email=?", (gearbox_email, ))
    return cur.fetchone()


def select_user_by_id(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE _id=?", (user_id, ))
    return cur.fetchone()


def remove_user_by_id(conn, user_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE _id=?", (user_id, ))
    conn.commit()
    cur.close()
