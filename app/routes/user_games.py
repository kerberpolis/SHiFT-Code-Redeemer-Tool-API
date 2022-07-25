import logging

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from app import database_controller
from app.config import get_config
from app.models.queries import user_id_path, user_game_id_path
from app.models.schemas import UserGame, UserGameResponse, ErrorResponse, UserGameFormData
from app.util import generate_uuid

db_conn = database_controller.create_connection()

router = APIRouter()


@router.get(
    get_config().BASE_PATH + '/user_games/{user_id}',
    tags=["user_game"],
    response_model=UserGameResponse,
    responses={
        422: {"model": ErrorResponse},
    }
)
def get_user_games(request: Request, user_id: int = user_id_path):
    # Query database
    try:
        sql = prepare_get_user_games()
        rows = query_database(sql, user_id)
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


@router.post(
    get_config().BASE_PATH + '/user_games',
    tags=["user_game"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def create_user_game(form_data: UserGameFormData):
    # Query database
    try:
        uuid = generate_uuid()
        row_id = database_controller.create_user_game(db_conn, uuid=uuid, user_id=form_data.user_id,
                                                      game=form_data.game, platform=form_data.platform)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Database error")

    # Parse results
    try:
        return UserGame(**{'_id': row_id, 'game': form_data.game,
                           'platform': form_data.platform, 'user_id': form_data.user_id})
    except Exception as e:  # noqa
        logging.error(e)
        raise HTTPException(status_code=500, detail="Parsing error")


@router.delete(
    get_config().BASE_PATH + '/user_games/{user_game_id}',
    tags=["user_game"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def delete_user_game(user_game_id: str = user_game_id_path):
    # Query database
    try:
        database_controller.delete_user_game(db_conn, user_game_id=user_game_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Database error")

    return True


def prepare_get_user_games():
    return """SELECT _id, game, platform, user_id FROM user_game WHERE user_id = :user_id"""


def query_database(sql: str, user_id: int):
    """Query database and return rows."""
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
