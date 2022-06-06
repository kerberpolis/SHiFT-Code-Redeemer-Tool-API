import app.database_controller as db
import pytest


@pytest.mark.parametrize(
    "codes_used, expected_codes_used",
    [
        (0, 0),
        (1, 1),
        (2, 2),
        (4, 4),
        (None, 5)  # None in list slice [:None] returns all
    ]
)
def test_user_used_codes(sqlite_connection, codes_used, expected_codes_used):
    # arrange
    users = db.select_all_users(sqlite_connection)
    codes = db.select_all_codes(sqlite_connection)
    user_codes = None
    code_ids = []

    # act
    if users[0]:
        for code in codes[:codes_used]:
            code_ids.append(code[0])
            db.create_user_code(sqlite_connection, users[0][0], code[0])

        user_codes = db.get_user_codes_by_id(sqlite_connection, users[0][0])

    # assert
    assert len(user_codes) == expected_codes_used
    for user_code in user_codes:
        assert user_code[1] in code_ids
        assert user_code[2] == users[0][0]
