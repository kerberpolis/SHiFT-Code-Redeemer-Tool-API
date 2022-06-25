import logging

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from app import database_controller
from app.config import get_config
from app.models.queries import user_id_path
from app.models.schemas import UserGame, UserGameResponse, ErrorResponse

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)

router = APIRouter()


@router.get(
    get_config().BASE_PATH + '/user/{user_id}/games',
    tags=["code"],
    response_model=UserGameResponse,
    responses={
        422: {"model": ErrorResponse},
    }
)
def get_user_games(request: Request, user_id: int = user_id_path):
    # Query database
    try:
        rows = query_database(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Database error")

    # Parse results
    try:
        data = parse_results(rows)
    except Exception as e:  # noqa
        logging.error(e)
        raise HTTPException(status_code=500, detail="Parsing error")

    # Prepare response
    try:
        response = prepare_response(request, data)
    except Exception as e:  # noqa
        logging.error(e)
        raise HTTPException(status_code=500, detail="Response preparation error")

    return response


def prepare_get_user_games():
    return """SELECT * FROM user_game WHERE user_id = :user_id"""


def query_database(user_id: int):
    """Query database and return rows."""
    sql = prepare_get_user_games()
    return database_controller.execute_sql(db_conn, sql, params={'user_id': user_id})


def parse_results(rows):
    """Parse rows into schema objects and get total rows"""
    return [UserGame(**row) for row in rows]


def prepare_response(request, data):
    """Package the data into a Response schema object"""
    response_data = {
        'msg': f'{len(data)} items returned',
        'type': 'success',
        'self': str(request.url),
        'data': data,
    }

    return UserGameResponse(**response_data)
