from sqlite3 import Connection

import requests

from app import database_controller
from app.util import convert_date
database = "borderlands_codes.db"
conn = database_controller.create_connection(database)


def json_archive(conn: Connection):
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
            'time_gathered': convert_date(code['archived']),
            'expires': convert_date(code['expires'])
        }
        database_controller.create_code(conn, code_data)


if __name__ == "__main__":
    json_archive(conn)
