from app.database_controller import create_user, select_user_by_id, remove_user_by_id


def test_create_and_remove_user(sqlite_connection, remove_users):
    # arrange
    user_data = {
        'gearbox_email': 'test_email',
        'gearbox_password': 'test_password',
        'salt': 'salt1'
    }

    # act
    user_id = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id)
    assert user[0] == user_id
    assert user[1] == user_data['gearbox_email']
    assert user[2] == user_data['gearbox_password']
    assert user[3] == user_data['salt']

    # act
    remove_user_by_id(sqlite_connection, user_id)

    # assert
    user = select_user_by_id(sqlite_connection, user_id)
    assert user is None


def test_create_user_with_same_gearbox_email(sqlite_connection, remove_users, capsys):
    # arrange
    user_data = {
        'gearbox_email': 'test_email',
        'gearbox_password': 'test_password',
        'salt': 'salt1'
    }

    # act
    user_id_1 = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id_1)
    assert user[0] == user_id_1
    assert user[1] == user_data['gearbox_email']

    # act
    create_user(sqlite_connection, user_data)
    captured = capsys.readouterr()
    assert "User could not be created due to Integrity issue." \
           " Error: UNIQUE constraint failed: users.gearbox_password" in captured.out
