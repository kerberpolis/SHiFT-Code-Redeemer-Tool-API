import logging
import logging.handlers
import threading
from sqlite3 import Connection

import app.borderlands_crawler as dtc
from app import config, database_controller
from app.borderlands_crawler import CodeFailedException, GameNotFoundException, \
    ConsoleOptionNotFoundException, GearBoxError

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)


def input_borderlands_codes(conn: Connection, user: tuple, codes: list):
    logged_in_borderlands = False
    crawler = dtc.BorderlandsCrawler(user)

    for row in codes:
        code = row[3]
        code_type = row[4]
        expiry_date = row[7]

        if expiry_date:  # allow all keys for now, even if supposedly expired, may still be redeemable
            try:
                if not logged_in_borderlands:
                    crawler.login_gearbox()
                    logged_in_borderlands = True
                result = crawler.input_code_gearbox(code)

                if result:
                    logging.info(f'Redeemed {code_type} code {code}')
                    # update expired attribute in codes table
                    database_controller.update_invalid_code(conn, row[0])
            except GearBoxError:
                logging.info(f'There was an error with gearbox when redeeming code {row[0]}, {code}')
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
            except Exception:
                pass
        else:
            database_controller.update_invalid_code(conn, row[0])
            print(f'This {code_type} code: {code}, has expired')

    crawler.tear_down()


def setup_logger():
    logging.basicConfig(filename='logger.log', level=logging.ERROR, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    # send error msg via email using googles smtp server
    # only works if google account does not have 2-factor authentication on.
    smtp_handler = logging.handlers.SMTPHandler(mailhost=("smtp.gmail.com", 587),
                                                fromaddr=config.EMAIL,
                                                toaddrs=[config.EMAIL],
                                                subject="Borderlands Auto Redeemer error!",
                                                credentials=(config.EMAIL, config.PASSWORD),
                                                secure=())
    logger = logging.getLogger()
    logger.addHandler(smtp_handler)


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
    valid_codes = database_controller.select_valid_codes(conn)

    if valid_codes:
        for user in database_controller.select_all_users(conn):
            thread = threading.Thread(target=input_borderlands_codes,
                                      name=f"borderlands_input_{user[0]}",
                                      args=(conn, user, valid_codes))
            thread.start()
            print(f'{thread.name} has started')


if __name__ == "__main__":
    setup_logger()
    setup_tables(db_conn)
    start_crawlers(db_conn)


