from starlette.requests import Request

from app.models.schemas import ErrorResponse, ErrorDetails


class InvalidParameterError(Exception):
    def __init__(self, request: Request, params: []):
        self.request = request
        self.params = params

    def response(self):
        response_data = {
            'msg': 'Invalid parameter fields',
            'type': 'bad request',
            'self': str(self.request.url),
            'errors': []
        }

        for param in self.params:
            err_data = {
                'param': param,
                'msg': 'parameter is not expected',
            }

            error_detail = ErrorDetails(**err_data)
            response_data['errors'].append(error_detail)

        response = ErrorResponse(**response_data)
        return response
