import os

from app.database_controller import encrypt, decrypt


def test_encrypt_password(sqlite_connection):
    # arrange
    key = os.getenv('BORDERLANDS_ENCRYPTION_KEY').encode()
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
