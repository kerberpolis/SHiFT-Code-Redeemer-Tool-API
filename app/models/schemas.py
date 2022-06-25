from pydantic import BaseModel, Field


class UserGameFormData(BaseModel):
    user_id: int = Field(..., example=1)
    game: str = Field(..., example="Borderlands 3")
    platform: str = Field(..., example="Epic")


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


class UserGame(BaseModel):
    _id: int = Field(..., example=1)
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    user_id: int = Field(..., example=1)


class UserCode(BaseModel):
    _id: int = Field(..., example=1)
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    user_id: int = Field(..., example=1)
    code_id: int = Field(..., example=110)
    is_redeem_success: int = Field(..., example=1)


class ErrorDetails(BaseModel):
    param: str
    msg: str


class MinimalResponse(BaseModel):
    msg: str
    type: str
    self: str


class CodeResponse(MinimalResponse):
    data: list[Code] = []


class UserCodeResponse(MinimalResponse):
    data: list[UserCode] = []


class UserGameResponse(MinimalResponse):
    data: list[UserGame] = []


class ErrorResponse(MinimalResponse):
    errors: list[ErrorDetails] = []
