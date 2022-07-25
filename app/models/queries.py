"""Shared FastAPI Query schemas.

Used for type and value validation of query parameters.
Used to generate JSON schemas and documentation for routes.
"""
from fastapi import Query
from fastapi import Path

code_query = Query(
    None,
    title='Code',
    description='The value of the SHiFT code.',
    example='BBF33-TFFWZ-KC3KW-3JJJJ-WCXZR'
)

token_query = Query(
    ...,
    title='Token',
    description='Token used to confirm user when registering.',
)


user_id_path = Path(
    ...,
    title='User ID',
    description='The ID of the user in the database.',
    example=1
)


user_game_id_path = Path(
    ...,
    title='User Game ID',
    description='The ID of the user game in the database.'
)
