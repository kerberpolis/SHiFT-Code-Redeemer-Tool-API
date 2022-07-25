from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class GearboxFormData(BaseModel):
    gearbox_email: str = Field(..., example='joe_bloggs@gmail.com')
    gearbox_password: str = Field(..., example='password')


class UserGameFormData(BaseModel):
    user_id: str = Field(..., example=1)
    game: str = Field(..., example="Borderlands 3")
    platform: str = Field(..., example="Epic")


class FeedbackData(BaseModel):
    title: str = Field(..., example='A bug has been found!')
    desc: str = Field(..., example='The bug is really bad!')
    page: str = Field(..., example='/path/to/page')
    browser: str = Field(..., example='firefox')
    browser_version: str = Field(..., example='88.0')
    width: str = Field(..., example='1000')
    height: str = Field(..., example='800')
    os: str = Field(..., example='unix')


class RegisterFormData(BaseModel):
    email: str = Field(..., example='joe_bloggs@gmail.com')
    password: str = Field(...)
    gearbox_email: str = Field(None, example='joe_bloggs_gearbox@gmail.com')
    gearbox_password: str = Field(None)


class UserFormData(BaseModel):
    email: str = Field(None, example='changed@gmail.com')
    password: str = Field(None)
    gearbox_email: str = Field(None)
    gearbox_password: str = Field(None)


class Code(BaseModel):
    id: int = Field(..., example=1, alias="_id")
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    code: str = Field(..., example='BBF33-TFFWZ-KC3KW-3JJJJ-WCXZR')
    type: str = Field(..., example='shift')
    reward: str = Field(..., example='1 skeleton key')
    time_gathered: str = Field(..., example='2022-06-24 14:41:47')
    expires: str = Field(..., example='2022-06-30 05:00:01')
    is_valid: int = Field(..., example=1)


class UserGame(BaseModel):
    id: str = Field(..., example=1, alias="_id")
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    user_id: str = Field(..., example=1)


class UserCode(BaseModel):
    _id: int = Field(..., example=1)
    game: str = Field(..., example='Wonderlands')
    platform: str = Field(..., example='Universal')
    user_id: str = Field(..., example=1)
    code_id: int = Field(..., example=110)
    is_redeem_success: int = Field(..., example=1)


class User(BaseModel):
    id: str = Field(..., example=1, alias="_id")
    email: str = Field(..., example='joe_bloggs@gmail.com')
    password: str = Field(...)
    gearbox_email: str = Field(None, example='joe_bloggs@gmail.com')
    gearbox_password: str = Field(None)
    notify_launch_game: int = Field(..., example=0)
    verified: int = Field(..., example=1)


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
