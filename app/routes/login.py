import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi import Response
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt

from app import database_controller
from app.config import get_config
from app.models.schemas import ErrorResponse
from app.models.schemas import Token, User
from app.util import decrypt

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "super_secret"
ALGORITHM = "HS256"

router = APIRouter()


@router.post(
    get_config().BASE_PATH + "/token",
    tags=["login"],
    response_model=Token,
    responses={
        422: {"model": ErrorResponse},
    })
def login_for_access_token(response: Response,
                           form_data: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=get_config().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.gearbox_email, expires_delta=access_token_expires)
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(login_email: str, login_password: str):
    user = get_user_by_email(login_email=login_email)
    if not user or not verify_password(login_password, user.gearbox_password):
        msg = 'Incorrect username or password'
        raise HTTPException(status_code=401, detail=msg)

    return user


def get_user_by_email(login_email: str):
    # Query database
    try:
        rows = database_controller.get_user_by_login_email(db_conn, login_email)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Database error")

    # Parse results
    try:
        user = parse_results(rows)
    except Exception as e:  # noqa
        logging.error(e)
        raise HTTPException(status_code=500, detail="Parsing error")

    return user


def verify_password(plain_password, encrypted_password):
    return plain_password == decrypt(encrypted_password.encode(), get_config().ENCRYPTION_KEY.encode()).decode()


def create_access_token(login_email: str, expires_delta: timedelta = 30):
    token_data = {
        "sub": login_email,
        "exp": datetime.utcnow() + expires_delta
    }
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        login_email = payload.get("sub")
        if login_email is None:
            raise credentials_exception
    except Exception:
        msg = 'Could not validate credentials'
        raise HTTPException(status_code=401, detail=msg)

    if login_email is None:
        msg = 'Could not validate credentials'
        raise HTTPException(status_code=401, detail=msg)

    user = get_user_by_email(login_email=login_email)
    if user is None:
        raise credentials_exception
    return user


def parse_results(row):
    """Parse rows into schema objects"""
    return User(**row)


@router.get(
    get_config().BASE_PATH + "/user",
    tags=["login"],
    response_model=User,
    responses={
        422: {"model": ErrorResponse},
    })
def get_user_login(user: User = Depends(get_current_user)):
    return user
