import threading

import pytest

from app.database_controller import create_user
from app.input_borderlands_codes import start_crawlers


# @pytest.mark.parametrize("users_data, expected_threads",
#      [
#          ([], 1),
#          ([
#             {'gearbox_email': 'test_email_1', 'gearbox_password': 'test_password_1', 'salt': 'salt_1'}
#           ], 2),
#          ([
#               {'gearbox_email': 'test_email_1', 'gearbox_password': 'test_password_1', 'salt': 'salt_1'},
#               {'gearbox_email': 'test_email_2', 'gearbox_password': 'test_password_2', 'salt': 'salt_2'},
#               {'gearbox_email': 'test_email_3', 'gearbox_password': 'test_password_3', 'salt': 'salt_3'},
#           ], 3)
#      ])
# def test_threads_created(users_data, expected_threads, sqlite_connection, remove_users):
#     # arrange
#     for user_data in users_data:
#         create_user(sqlite_connection, user_data)
#
#     # act
#     start_crawlers(sqlite_connection)
#
#     # assert
#     assert threading.active_count() == expected_threads
