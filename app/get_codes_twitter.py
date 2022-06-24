import logging
import logging.handlers
import re
from datetime import datetime
from sqlite3 import Connection

import tweepy
from tweepy import OAuthHandler
from tweepy.models import Status

from app import database_controller
from app.config import get_config, AppConfig
from app.util import convert_date

database = "borderlands_codes.db"
conn = database_controller.create_connection(database)


def get_shift_tweets(conn: Connection, config: AppConfig = get_config()):
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

            code_data = {
                'game': game,
                'platform': platform,
                'code': code,
                'type': code_type,
                'reward': reward,
                'time_gathered': datetime.now(),
                'expires': expires
            }
            database_controller.create_code(conn, code_data)


def get_reward(text: str) -> str:
    regexp = re.compile(r'Reward: (.*?(?=\n{1,}))')
    reward_match = re.search(regexp, text)
    if reward_match:
        return reward_match.group(1)

    return "Unknown"


def get_game(text: str) -> str:
    game_regexp = re.compile(r'Game: (WONDERLANDS|BORDERLANDS:?\s([2-3]|[A-Z]+-[A-Z]+))')
    game_match = re.search(game_regexp, text)
    if game_match:
        return game_match.group(1).title()

    return "Unknown"


def get_code(text: str) -> (str, str):
    shift_regexp = re.compile(r'[Xbox:\s]?(([A-Z\d]{5}-){4}[A-Z\d]{5})')
    shift_match = re.search(shift_regexp, text)
    if shift_match:
        return "shift", shift_match.group(1)

    return None, None


def get_expiration(text: str) -> str:
    regexp = re.compile(r'Expires: (.*?(?=\n{1,}))')
    expiry_match = re.search(regexp, text)
    try:
        if expiry_match.group(1):
            return convert_date(expiry_match.group(1))
    except AttributeError:
        pass

    return "Unknown"


def parse_tweet(tweet: Status):
    text = tweet.full_text
    game = get_game(text)
    code_type, code = get_code(text)
    reward = get_reward(text)
    expires = get_expiration(text)

    return game, code_type, code, reward, expires


if __name__ == "__main__":
    get_shift_tweets(conn)
