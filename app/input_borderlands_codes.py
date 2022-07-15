import logging
import logging.handlers
import threading
from sqlite3 import Connection
from app.models.schemas import User, Code
import app.borderlands_crawler as dtc
from app import database_controller
from app.borderlands_crawler import CodeFailedException, GameNotFoundException, \
    PlatformOptionNotFoundException, GearboxShiftError, GearboxUnexpectedError, \
    ShiftCodeAlreadyRedeemedException, InvalidCodeException, \
    CodeExpiredException, CodeNotAvailableException, GearboxLoginError

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)


def input_borderlands_codes(conn: Connection, user: tuple, games: dict):
    logged_in_borderlands = False
    valid_codes = database_controller.get_valid_codes_by_user(conn, user[0])
    if valid_codes:
        user = User(**user)
        crawler = dtc.BorderlandsCrawler(user=user.dict(), headless=False)
        for row in valid_codes:
            code = Code(**row)
            shift_code = code.code
            user_id, code_id = user.id, code.id

            # allow all keys for now, even if supposedly expired, may still be redeemable
            try:
                # for x in range(2):  # attempt to log in to gearbox site twice
                if not logged_in_borderlands:
                    logged_in_borderlands = crawler.login_gearbox()
            except Exception as e:  # catch exceptions when logging into gearbox website
                print(f'Exception occurred when logging into gearbox site: {e.args}')

            if not logged_in_borderlands:  # if still not logged in teardown and raise exception
                crawler.tear_down()
                raise GearboxLoginError()

            game, platform = None, None
            try:
                games_available = crawler.get_games_to_redeem_for_code(shift_code)
                if games_available:
                    # Sometimes there can be more than 1 title the code can be redeemed
                    # for (ZFKJ3-TT3BB-JTBJT-T3JJT-JWX9H). Loop through the games and redeem for each one.
                    for idx, game_available in enumerate(games_available):
                        game = game_available
                        try:  # find the platform the user wants to redeem the code for
                            platform = games[game]
                        except KeyError:
                            # if no game is found for user to redeem code, throw exception
                            raise GameNotFoundException(game)

                        if idx > 0:
                            crawler.input_shift_code(shift_code)  # insert the code into the input box
                        # redeem the code for that platform
                        result = crawler.redeem_shift_code(shift_code, game, platform)
                        if result:
                            logging.info(f'Redeemed code {shift_code}')
                            # add row to user_code table showing user_id has used a code
                            user_code_id = database_controller.create_user_code(conn, user_id, code_id,
                                                                                game, platform, 1)
                            if user_code_id:
                                print(f'User {user_id} has successfully used code {code_id}')
            except GearboxUnexpectedError as e:
                logging.debug(f'There was an error with gearbox when redeeming code {code_id}, {shift_code}.')
                logging.debug(e.args[0])
                return
            except GearboxShiftError as e:
                logging.debug(f'There was an error with gearbox when redeeming code {code_id}, {shift_code}.')
                logging.debug(e.args[0])
                database_controller.set_notify_launch_game(conn, 1, user_id)
                return
            except PlatformOptionNotFoundException as e:
                logging.info(str(e))
                logging.info(f'Code {code_id} cannot be redeemed on {platform}.')
                database_controller.create_user_code(conn, user_id, code_id,
                                                     game, platform, 0)
            except GameNotFoundException:
                logging.info(f'Code {code_id} cannot be redeemed for user {user_id} as '
                             f'they do not have a platform set to redeem it on.')
            except CodeFailedException as e:
                logging.info(str(e))
                print(e)
                # this exception currently handles code exceptions that may require different handling.
            except CodeNotAvailableException as e:
                print(e.args[0])
                database_controller.create_user_code(conn, user_id, code_id,
                                                     game, platform, 0)
            except ShiftCodeAlreadyRedeemedException:
                print('This Shift code has already been redeemed.')
                database_controller.create_user_code(conn, user_id, code_id,
                                                     game, platform, 1)
            except (InvalidCodeException, CodeExpiredException):
                print(f"Shift code {code_id} is no longer valid. Setting to invalid.")
                database_controller.update_invalid_code(conn, code_id)
            except Exception as e:
                print(f'Default Exception: {e}')

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
    for user in database_controller.select_all_users_with_gearbox(conn):
        if user[5] == 1:
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
