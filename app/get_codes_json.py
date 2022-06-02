import requests

from app import database_controller

database = "borderlands_codes.db"
conn = database_controller.create_connection(database)


def json_archive(conn):
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


if __name__ == "__main__":
    json_archive(conn)
