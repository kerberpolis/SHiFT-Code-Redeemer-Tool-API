"""Shared FastAPI Query schemas.

Used for type and value validation of query parameters.
Used to generate JSON schemas and documentation for routes.
"""
from fastapi import Query


code_query = Query(
    None,
    title='Code',
    description='The value of the SHiFT code.',
    example='BBF33-TFFWZ-KC3KW-3JJJJ-WCXZR'
)
