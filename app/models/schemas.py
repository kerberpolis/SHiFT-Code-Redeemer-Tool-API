from pydantic import BaseModel, Field


class Code(BaseModel):
    _id: int = Field(..., example=1)
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    code: str = Field(..., example='BBF33-TFFWZ-KC3KW-3JJJJ-WCXZR')
    type: str = Field(..., example='shift')
    reward: str = Field(..., example='1 skeleton key')
    time_gathered: str = Field(..., example='2022-06-24 14:41:47')
    expires: str = Field(..., example='2022-06-30 05:00:01')
    is_valid: int = Field(..., example=1)


class ErrorDetails(BaseModel):
    param: str
    msg: str


class MinimalResponse(BaseModel):
    msg: str
    type: str
    self: str


class CodeResponse(MinimalResponse):
    data: list[Code] = []


class ErrorResponse(MinimalResponse):
    errors: list[ErrorDetails] = []