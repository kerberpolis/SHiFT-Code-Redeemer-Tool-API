import logging
import sqlite3
from sqlite3 import Error, Connection


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
    except Error as e:
        print(e)

    return conn


def execute_sql(conn: Connection, sql: str, params: dict = None):
    """
    Query all rows in the codes table
    """
    cur = conn.cursor()
    with conn:
        cur.execute(sql, params)
    return cur.fetchall()


def create_user_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS user(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                gearbox_email TEXT NOT NULL UNIQUE,
                gearbox_password TEXT NOT NULL UNIQUE,
                notify_launch_game INTEGER CHECK(notify_launch_game IN (0, 1)) NOT NULL DEFAULT 0
            )"""

    create_table(conn, sql)


def create_code_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS code(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                game TEXT,
                platform TEXT,
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                reward TEXT DEFAULT Unknown,
                time_gathered TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires TEXT,
                is_valid INT NOT NULL DEFAULT 1,
                UNIQUE(game, code)
            )"""

    create_table(conn, sql)


def create_user_game_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS user_game(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                game TEXT NOT NULL,
                platform TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                UNIQUE(game, platform, user_id),
                FOREIGN KEY (user_id) REFERENCES user (_id)
            )"""

    create_table(conn, sql)


def create_user_code_table(conn: Connection):
    sql = """CREATE TABLE IF NOT EXISTS user_code(
                _id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                code_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                game TEXT,
                platform TEXT,
                is_redeem_success INTEGER NOT NULL,
                UNIQUE(user_id, code_id, game, platform),
                FOREIGN KEY (code_id) REFERENCES code (_id),
                FOREIGN KEY (user_id) REFERENCES user (_id)
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
    Create a new code into the code table.
    """
    sql = '''INSERT INTO code(game, platform, code, type, reward, time_gathered, expires)
             VALUES(:game, :platform, :code, :type, :reward, :time_gathered, :expires)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, code_data)
        conn.commit()
        print(f'Creating {code_data["game"]} code {code_data["code"]} in database table code')
    except sqlite3.IntegrityError as e:
        # cannot add due to unique constraint
        print(f'{code_data["type"]} code {code_data["code"]} already exists. Error: {str(e)}')
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
    sql = '''UPDATE code
             SET is_valid = 0
             WHERE _id = ?'''

    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id, ))
    cur.close()


def delete_code(conn: Connection, code_id: int):
    """
    Delete a code by code id
    """
    sql = 'DELETE FROM code WHERE _id=?'
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (code_id,))
    cur.close()


def delete_all_codes(conn: Connection):
    """
    Delete all rows in the codes table
    """
    sql = 'DELETE FROM code'
    cur = conn.cursor()
    with conn:
        cur.execute(sql)
    cur.close()


def select_valid_codes(conn: Connection):
    """
    Query codes by validity
    """
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM code WHERE is_valid=1")
    rows = cur.fetchall()

    cur.close()

    return rows


def select_code_by_id(conn: Connection, code_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM code WHERE _id=?", (code_id, ))
    rows = cur.fetchall()

    return rows


def create_user(conn: Connection, user_data: dict):
    sql = '''INSERT INTO user(gearbox_email, gearbox_password)
                 VALUES(:gearbox_email, :gearbox_password)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, user_data)
        conn.commit()
        print(f'Creating User {user_data["gearbox_email"]} in database table user')
    except sqlite3.IntegrityError as e:
        print(f'User {user_data["gearbox_email"]} could not be created due to Integrity issue. Error: {str(e)}')
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def select_all_users(conn: Connection):
    cur = conn.cursor()
    cur.execute('SELECT * FROM user')
    return cur.fetchall()


def get_user_by_login_email(conn: Connection, login_email: str):
    cur = conn.cursor()
    cur.execute('SELECT * FROM user WHERE LOWER(gearbox_email) = LOWER(:login_email)', (login_email, ))
    return cur.fetchone()


def select_users_by_launch_notification(conn: Connection, launch_bool: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM user WHERE notify_launch_game = ?', (launch_bool,))
    return cur.fetchall()


def select_user_by_gearbox_email(conn: Connection, gearbox_email: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE gearbox_email=?", (gearbox_email, ))
    return cur.fetchone()


def select_user_by_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE _id=?", (user_id, ))
    return cur.fetchone()


def remove_user_by_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM user WHERE _id=?", (user_id, ))
    conn.commit()
    cur.close()


def create_user_code(conn: Connection, user_id: int, code_id: int,
                     game: str, platform: str, is_success: int):
    """
    A user has used a particular code successfully. Create a row in user_code table
    to record this.
    :param conn: db connection
    :param user_id: id of the user using the code
    :param code_id: id of the code
    :param game: the game the code is being redeemed for
    :param platform: platform the user redeemed the code for
    :param is_success: an int representing a bool if the code was successfully redeemed or not
    :return: the id of the last row created
    """
    sql = '''INSERT INTO user_code(user_id, code_id, game, platform, is_redeem_success)
                     VALUES(:user_id, :code_id, :game, :platform, :is_success)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, (user_id, code_id, game, platform, is_success))
        conn.commit()
        print(f'Creating user code for user {user_id} and code {code_id} for {game} on {platform}. Code was'
              f' {"successfully" if is_success == 1 else "unsuccessfully"} redeemed.')
    except sqlite3.IntegrityError as e:
        print(f'User {user_id} has already used code {code_id}. Error: {str(e)}')
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def get_user_codes_by_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_code WHERE user_id=?', (user_id, ))
    return cur.fetchall()


def get_valid_codes_by_user(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM code WHERE _id NOT IN ('
                'SELECT code_id FROM user_code WHERE user_id=?1)'
                'AND game IN ('
                'SELECT game FROM user_game WHERE user_id=?1)'
                'AND is_valid = 1', (user_id,))
    return cur.fetchall()


def get_successful_codes_by_user_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM code WHERE _id IN ('
                'SELECT code_id FROM user_code WHERE user_id=? AND is_redeem_success = 1)'
                'ORDER BY game DESC', (user_id,))
    return cur.fetchall()


def get_unsuccessful_codes_by_user_id(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM code WHERE _id IN ('
                'SELECT code_id FROM user_code WHERE user_id=? AND is_redeem_success = 0)', (user_id,))
    return cur.fetchall()


def set_notify_launch_game(conn: Connection, launch_bool: int, user_id: int) -> None:
    """
    Update user column notify_launch_game. Values of 1 will be emailed to inform them they
    must launch a Borderlands title.
    """
    sql = '''UPDATE user
             SET notify_launch_game = ?
             WHERE _id = ?'''
    cur = conn.cursor()
    with conn:
        cur.execute(sql, (launch_bool, user_id,))
    cur.close()


def create_user_game(conn: Connection, game: str, platform: str, user_id: int):
    """
    A user can set preference for what platform a shift code enabled game can be redeemed for.

    :param conn: db connection
    :param game: The shift code game to redeem the code.
    :param platform: The platform for the game to redeem on.
    :param user_id: id of the user using the code.
    :return: the id of the last row created.
    """
    sql = '''INSERT INTO user_game(game, platform, user_id)
                     VALUES(:game, :platform, :user_id)'''
    cur = conn.cursor()

    try:
        with conn:
            cur.execute(sql, (game, platform, user_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f'User {user_id} has game {game} preference set to {platform} already. Error: {str(e)}')
    except sqlite3.DatabaseError as e:
        print(f'Database Error: {str(e)}')
        conn.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        conn.rollback()

    return cur.lastrowid


def get_user_games(conn: Connection, user_id: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_game WHERE user_id=?', (user_id,))
    return cur.fetchall()


def delete_user_game(conn: Connection, user_game_id: int):
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM user_game WHERE _id=?', (user_game_id,))
        conn.commit()
        cur.close()
    except Exception as e:
        print(e)
        return False
        
    return True
