import logging

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from app import database_controller
from app.config import get_config
from app.models.schemas import Code, CodeResponse, ErrorResponse

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)

router = APIRouter()


@router.get(
    get_config().BASE_PATH + '/codes',
    tags=["code"],
    response_model=CodeResponse,
    responses={
        422: {"model": ErrorResponse},
    }
)
def get_codes(request: Request):
    # Query database
    try:
        rows = query_database()
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


def query_database():
    """Query database and return rows."""
    rows = database_controller.select_all_codes(db_conn)
    return rows


def parse_results(rows):
    """Parse rows into schema objects and get total rows"""
    return [Code(**row) for row in rows]


def prepare_response(request, data):
    """Package the data into a Response schema object"""
    response_data = {
        'msg': f'{len(data)} items returned',
        'type': 'success',
        'self': str(request.url),
        'data': data,
    }

    return CodeResponse(**response_data)
