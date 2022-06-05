from app.database_controller import create_user, select_user_by_id, remove_user_by_id, encrypt, decrypt
import os


def test_create_and_remove_user(sqlite_connection, remove_users):
    # arrange
    user_data = {
        'gearbox_email': 'test_email',
        'gearbox_password': 'test_password',
    }

    # act
    user_id = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id)
    assert user[0] == user_id
    assert user[1] == user_data['gearbox_email']
    assert user[2] == user_data['gearbox_password']

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
    }

    # act
    user_id_1 = create_user(sqlite_connection, user_data)

    # assert
    user = select_user_by_id(sqlite_connection, user_id_1)

    print(user)
    print(type(user))

    assert user[0] == user_id_1
    assert user[1] == user_data['gearbox_email']

    # act
    create_user(sqlite_connection, user_data)
    captured = capsys.readouterr()
    assert "User could not be created due to Integrity issue." \
           " Error: UNIQUE constraint failed: users.gearbox_password" in captured.out


def test_encrypt_password(sqlite_connection):
    # arrange
    key = os.getenv('BORDERLANDS_USER_CRYPTOGRAPHY_KEY').encode()
    password = 'test_password'

    # act
    token = encrypt(password.encode(), key)

    # assert
    assert type(token) == bytes

    # act
    msg = decrypt(token, key)

    # assert
    assert type(msg) == bytes
    assert msg.decode() == password

