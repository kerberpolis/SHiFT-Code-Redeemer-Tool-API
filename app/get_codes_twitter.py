import logging
import logging.handlers
import re
from datetime import datetime

import pytz
import tweepy
from tweepy import OAuthHandler

from app import config
from app import database_controller

database = "borderlands_codes.db"
conn = database_controller.create_connection(database)


def twitter_stream(conn):
    auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name='dgSHiFTCodes', count=200,
                               exclude_replies=True, include_rts=False, tweet_mode='extended')

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
            if code_type == "shift" and not platform and game in ["Borderlands 3", 'Wonderlands']:
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
        return "shift", shift_match.group(1)

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


if __name__ == "__main__":
    twitter_stream(conn)
