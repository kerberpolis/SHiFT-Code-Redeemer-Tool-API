import logging
import logging.handlers
import threading
from sqlite3 import Connection

import app.borderlands_crawler as dtc
from app import database_controller
from app.borderlands_crawler import CodeFailedException, GameNotFoundException, \
    ConsoleOptionNotFoundException, GearboxShiftError, GearboxUnexpectedError

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)


def input_borderlands_codes(conn: Connection, user: tuple):
    logged_in_borderlands = False
    crawler = dtc.BorderlandsCrawler(user)

    for row in database_controller.get_valid_user_codes(conn, user[0]):
        code = row[3]
        code_type = row[4]
        expiry_date = row[7]

        if expiry_date:  # allow all keys for now, even if supposedly expired, may still be redeemable
            user_id, code_id = user[0], row[0]
            try:
                if not logged_in_borderlands:
                    crawler.login_gearbox()
                    logged_in_borderlands = True
            except Exception as e:  # todo: catch exceptions when logging into gearbox website
                print(f'Default Exception: {e.args}')

            try:
                result = crawler.input_code_gearbox(code)
                if result:
                    logging.info(f'Redeemed {code_type} code {code}')
                    # update expired attribute in codes table
                    database_controller.update_invalid_code(conn, row[0])

                    # add row to user_code table showing user_id has used a code
                    user_code_id = database_controller.create_user_code(conn, user_id, code_id)
                    if user_code_id:
                        print(f'User {user_id} has successfully used code {code_id}')
            except GearboxUnexpectedError as e:
                logging.debug(f'There was an error with gearbox when redeeming code {row[0]}, {code}.')
                logging.debug(e.args[0])
                return
            except GearboxShiftError as e:
                logging.debug(f'There was an error with gearbox when redeeming code {row[0]}, {code}.')
                logging.debug(e.args[0])
            except ConsoleOptionNotFoundException as e:
                logging.info(str(e))
                database_controller.update_invalid_code(conn, row[0])
            except GameNotFoundException as e:
                logging.info(f'Code {code} cannot be redeemed as code is for a game '
                             f'you do not own. {str(e)} game is not valid ')
                database_controller.update_invalid_code(conn, row[0])
            except CodeFailedException as e:
                logging.info(str(e))
                database_controller.update_invalid_code(conn, row[0])
                database_controller.create_user_code(conn, user_id, code_id)
            except Exception as e:
                print(f'Default Exception: {e}')

        else:
            database_controller.update_invalid_code(conn, row[0])
            print(f'This {code_type} code: {code}, has expired')

    crawler.tear_down()


def setup_logger():
    logging.basicConfig(filename='logger.log', level=logging.ERROR, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger()


def setup_tables(conn: Connection):
    """
    Create tables in sqlite database
    """
    if conn is not None:
        database_controller.create_code_table(conn)
        database_controller.create_user_table(conn)
        database_controller.create_user_code_table(conn)
    else:
        print("Error! cannot create the database connection.")


def start_crawlers(conn: Connection):
    for user in database_controller.select_all_users(conn):
        thread = threading.Thread(target=input_borderlands_codes,
                                  name=f"borderlands_input_{user[0]}",
                                  args=(conn, user))
        print(f'{thread.name} starting.')
        thread.start()
        thread.join()


if __name__ == "__main__":
    setup_logger()
    setup_tables(db_conn)
    start_crawlers(db_conn)
