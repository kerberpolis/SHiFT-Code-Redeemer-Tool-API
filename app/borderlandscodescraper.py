import logging
import logging.handlers
import re
import threading
import time
from datetime import datetime

import pytz
import requests
import tweepy
from tweepy import OAuthHandler

import app.borderlands_crawler as dtc
from app import config, database_controller
from app.borderlands_crawler import CodeFailedException, GameNotFoundException, \
    ConsoleOptionNotFoundException, GearBoxError

database = "borderlands_codes.db"
conn = database_controller.create_connection(database)


def twitter_stream(conn):
    auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name='dgSHiFTCodes', count=200,
                               exclude_replies=True, include_rts=False, tweet_mode='extended')

    # with open('app/tweets.csv', 'a', encoding='utf-8') as f:
    #     for tweet in tweets:
    #         # tweets_list.append(tweet.text)
    #         f.write(tweet.full_text+'\n\n')
    #         print(tweet.full_text)
    #         # print(tweet)

    for tweet in tweets:
        code_type, code, game, reward, platform, expires = None, None, None, None, None, None

        try:
            game, code_type, code, reward, expires = parse_tweet(tweet)
        except KeyError as e:
            msg = f'Error on_data: {str(e)},\n data: {tweet}'
            print(msg)
            logging.error(msg, exc_info=True)

        # if tweet contains relevant information, create code
        if code_type and code:
            if code_type == "SHiFT" and not platform and game in ["Borderlands 3", 'Wonderlands']:
                platform = "Universal"
            else:
                platform = "Xbox"

            database_controller.create_code(conn, (game, platform, code,
                                            code_type, reward, datetime.now(),
                                            expires))


def get_reward(text):
    regexp = re.compile(r'Reward: (.*?(?=\n{1,}))')
    reward_match = re.search(regexp, text)
    if reward_match:
        return reward_match.group(1)

    return "Unknown"


def get_game(text):
    game_regexp = re.compile(r'Game: (WONDERLANDS|BORDERLANDS:?\s([2-3]|[A-Z]+-[A-Z]+))')
    game_match = re.search(game_regexp, text)
    if game_match:
        return game_match.group(1).title()

    return "Unknown"


def get_code(text):
    shift_regexp = re.compile(r'[Xbox:\s]?(([A-Z\d]{5}-){4}[A-Z\d]{5})')
    shift_match = re.search(shift_regexp, text)
    if shift_match:
        return "SHiFT", shift_match.group(1)

    return None, None


#  todo: parse datetime expiration date in tweet. expiration is not always present. Most seem to be in UTC so far.
def get_date(str_date):
    tzone_dic = {
        'PST': '-0800',
        'PDT': '-0700',
        'MST': '-0700',
        'MDT': '-0600',
        'CST': '-0600',
        'CDT': '-0500',
        'EST': '-0500',
        'EDT': '-0400',
    }

    # datetime does not recognise PST, CST, EST etc for dt formating using %Z,
    # instead use dict to replace the tz with UTC offset, %z.
    if any(tzone in str_date for tzone in tzone_dic.keys()):
        for key in tzone_dic.keys():
            if key in str_date:
                str_date = str_date.replace(key, tzone_dic[key])

    # 11 Jan 14:00 Sunday, 11 Jan 13:00, 11 Jan, 11 JUNE, 2 JUN 07:59 UTC, 20 APR 23:59 -0500
    # 26 May 2022 17:30:00 -0400
    date_patterns = ['%d %b %Y %H:%M %Z', '%d %b %H:%M %A', '%d %b %H:%M', '%d %b', '%d %B',
                     '%d %b %H:%M %Z', '%d %b %H:%M %z', '%d %b %H:%M %Z']

    for pattern in date_patterns:
        try:
            dt = datetime.strptime(str_date, pattern)
            if dt.tzinfo:
                # convert dt to utc
                dt = datetime.strptime(dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                       "%Y-%m-%d %H:%M:%S")

            # It's {CURRENT YEAR}! replace dt year (1900) with current year
            dt = dt.replace(year=datetime.now().year)
            return dt
        except ValueError:
            pass
        except pytz.UnknownTimeZoneError:
            print('Unknown timezone')
            pass

    print("Date not in expected format")
    return "Unknown"


def get_expiration(text):
    regexp = re.compile(r'Expires: (.*?(?=\n{1,}))')
    expiry_match = re.search(regexp, text)
    try:
        if expiry_match.group(1):
            return get_date(expiry_match.group(1))
    except AttributeError:
        pass

    return "Unknown"


#  todo: text contains \n\n, messes w regex.
def parse_tweet(tweet):
    text = tweet.full_text
    game = get_game(text)
    code_type, code = get_code(text)
    reward = get_reward(text)
    expires = get_expiration(text)

    return game, code_type, code, reward, expires


def input_borderlands_codes(conn):
    while True:
        time.sleep(2)
        valid_codes = database_controller.select_valid_codes(conn)
        if valid_codes:
            logged_in_borderlands = False
            crawler = dtc.BorderlandsCrawler()

            for row in valid_codes:
                code = row[3]
                code_type = row[4]
                expiry_date = row[7]
                # if expiry_date not in ("Unknown", "unknown", "0"):
                #     expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')

                # if code has not expired or unknown
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
                    # database_controller.update_invalid_code(conn, row[0])
                    print(f'This SHiFT code: {code}, has expired')

            time.sleep(1)
            crawler.tear_down()
            time.sleep(1800)


def json_archive(conn):
    while True:
        url = 'https://shift.orcicorn.com/shift-code/index.json'

        # creating HTTP response object from given url
        resp = requests.get(url)
        codes = resp.json()[0]['codes']

        for code in codes:
            code_data = {
                'game': code['game'],
                'platform': code['platform'],
                'code': code['code'],
                'type': code['type'],
                'reward': code['reward'],
                'time_gathered': code['archived'],
                'expires': code['expires']
            }
            database_controller.create_code(conn, code_data)

        time.sleep(900)


def setup_logger():
    logging.basicConfig(filename='logger.log', level=logging.ERROR, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    # send error msg via email using googles smtp server
    # only works if google account does not have 2 factor authentication on.
    smtp_handler = logging.handlers.SMTPHandler(mailhost=("smtp.gmail.com", 587),
                                                fromaddr=config.EMAIL,
                                                toaddrs=[config.EMAIL],
                                                subject="Borderlands Auto Redeemer error!",
                                                credentials=(config.EMAIL, config.PASSWORD),
                                                secure=())
    logger = logging.getLogger()
    logger.addHandler(smtp_handler)


def setup_tables():
    """
    Create tables in sqlite database
    """
    if conn is not None:
        database_controller.create_code_table(conn)
        database_controller.create_user_table(conn)
    else:
        print("Error! cannot create the database connection.")


if __name__ == "__main__":
    setup_logger()
    setup_tables()

    thread_list = []
    t1 = threading.Thread(target=twitter_stream, name='twitter_streamer', args=(conn,))
    thread_list.append(t1)
    t2 = threading.Thread(target=json_archive, name="json_archive", args=(conn,))
    thread_list.append(t2)
    t3 = threading.Thread(target=input_borderlands_codes, name="borderlands_input", args=(conn,))
    thread_list.append(t3)

    # for t in thread_list:
    #     t.start()
    #     print(f'{t.name} has started')
