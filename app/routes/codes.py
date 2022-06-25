import logging

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from app import database_controller
from app.config import get_config
from app.errors import InvalidParameterError
from app.models.queries import code_query
from app.models.schemas import Code, CodeResponse, ErrorResponse

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)

PARAM_FILTERS = dict(
    code="AND CODE = :code",
)

router = APIRouter()


@router.get(
    get_config().BASE_PATH + '/codes',
    tags=["code"],
    response_model=CodeResponse,
    responses={
        422: {"model": ErrorResponse},
    }
)
def get_codes(request: Request, code: str = code_query):
    # Validate inputs
    valid_params = {"code"}
    request_params = set(request.query_params.keys())
    bad_params = request_params - valid_params
    if bad_params:
        raise InvalidParameterError(request=request, params=bad_params)

    # Collect parameters used in this request
    request_params = {}
    for param_name in valid_params:
        if locals()[param_name] is not None:
            request_params[param_name] = locals()[param_name]

    # Query database
    try:
        rows = query_database(request_params)
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


def prepare_select_codes_query(params: list) -> str:
    filters = {}
    for filter_name in PARAM_FILTERS:
        if filter_name in params:
            filters[filter_name] = PARAM_FILTERS[filter_name]
        else:
            filters[filter_name] = ''

    template = """SELECT * FROM code
                    WHERE 1 = 1
                    {code}
    """

    return template.format(**filters)


def query_database(request_params):
    """Query database and return rows."""
    sql = prepare_select_codes_query(request_params.keys())
    rows = database_controller.select_all_codes(db_conn, sql=sql, params=request_params)

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
