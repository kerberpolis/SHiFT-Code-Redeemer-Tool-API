import logging
import logging.handlers
import threading
from sqlite3 import Connection

import app.borderlands_crawler as dtc
from app import database_controller
from app.borderlands_crawler import CodeFailedException, GameNotFoundException, \
    PlatformOptionNotFoundException, GearboxShiftError, GearboxUnexpectedError, \
    ShiftCodeAlreadyRedeemedException, InvalidCodeException, \
    CodeExpiredException

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)


def input_borderlands_codes(conn: Connection, user: tuple, games: dict):
    logged_in_borderlands = False
    crawler = dtc.BorderlandsCrawler(user, games)

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
                database_controller.set_notify_launch_game(conn, 1, user_id)
                return
            except PlatformOptionNotFoundException as e:
                logging.info(str(e))
                # database_controller.create_user_code(conn, user_id, code_id)
            except GameNotFoundException:
                logging.info(f'Code {code_id} cannot be redeemed for user {user_id} as they do not have a platform '
                             f'set to redeem it on.')
                # database_controller.create_user_code(conn, user_id, code_id)
            except CodeFailedException as e:
                logging.info(str(e))
                # this exception currently handles code exceptions that may require different handling.

                # database_controller.update_invalid_code(conn, row[0])
                # database_controller.create_user_code(conn, user_id, code_id)
            except ShiftCodeAlreadyRedeemedException:
                database_controller.create_user_code(conn, user_id, code_id)
            except (InvalidCodeException, CodeExpiredException):
                database_controller.update_invalid_code(conn, code_id)
            except Exception as e:
                print(f'Default Exception: {e}')

        else:
            database_controller.update_invalid_code(conn, row[0])
            print(f'This {code_type} code: {code}, has expired')

    crawler.tear_down()


def setup_logger():
    logging.basicConfig(filename='logger.log', level=logging.ERROR, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logging.getLogger()


def setup_tables(conn: Connection):
    """
    Create tables in sqlite database
    """
    if conn is not None:
        database_controller.create_code_table(conn)
        database_controller.create_user_table(conn)
        database_controller.create_user_code_table(conn)
        database_controller.create_user_game_table(conn)
    else:
        print("Error! cannot create the database connection.")


def start_crawlers(conn: Connection):
    for user in database_controller.select_all_users(conn):
        if user[3] == 1:
            print(f'User {user[1]} cannot enter shift codes until they launch a Borderlands title.'
                  f' Sending notification email.')

        user_games = parse_user_games(database_controller.get_user_games(conn, user[0]))
        thread = threading.Thread(target=input_borderlands_codes,
                                  name=f"borderlands_input_{user[0]}",
                                  args=(conn, user, user_games))
        print(f'{thread.name} starting.')
        thread.start()
        thread.join()


def parse_user_games(user_games: list):
    user_games_dic = dict()
    for game in user_games:
        user_games_dic[game[1]] = game[2]

    return user_games_dic


if __name__ == "__main__":
    setup_logger()
    setup_tables(db_conn)
    start_crawlers(db_conn)
