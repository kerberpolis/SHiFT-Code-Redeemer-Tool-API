from app.database_controller import create_user, select_user_by_id, remove_user_by_id


def test_create_and_remove_user(sqlite_connection):
    # arrange
    user_data = {
        'email': 'test_email',
        'password': 'test_password',
        'gearbox_email': 'test_gearbox_email',
        'gearbox_password': 'test_gearbox_password',
    }

    # act
    user_id = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id)
    assert user[0] == user_id
    assert user[1] == user_data['email']
    assert user[2] == user_data['password']
    assert user[3] == user_data['gearbox_email']
    assert user[4] == user_data['gearbox_password']

    # act
    remove_user_by_id(sqlite_connection, user_id)

    # assert
    user = select_user_by_id(sqlite_connection, user_id)
    assert user is None


def test_create_user_with_same_gearbox_email(sqlite_connection, capsys):
    # arrange
    user_data = {
        'email': 'test_email',
        'password': 'test_password',
        'gearbox_email': 'test_gearbox_email',
        'gearbox_password': 'test_gearbox_password',
    }

    # act
    user_id_1 = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id_1)

    assert user[0] == user_id_1
    assert user[1] == user_data['email']

    # act
    create_user(sqlite_connection, user_data)
    captured = capsys.readouterr()
    assert f"User {user_data['email']} could not be created due to Integrity issue." \
           " Error: UNIQUE constraint failed: user.email, user.gearbox_email" in captured.out
