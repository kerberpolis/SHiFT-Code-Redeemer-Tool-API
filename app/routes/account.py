import logging
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from app import database_controller
from app.config import get_config, AppConfig
from app.models.schemas import GearboxFormData, UserFormData, ErrorResponse
from app.models.queries import token_query
from app.borderlands_crawler import BorderlandsCrawler
from app.util import encrypt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from passlib.pwd import genword
import hashlib
from app.util import generate_uuid
from app.errors import InvalidParameterError

conf = ConnectionConfig(
    MAIL_USERNAME="danielhsutton",
    MAIL_PASSWORD="pevngbfpftrhobsk",
    MAIL_FROM="SHiFTCodeRedeemer@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_FROM_NAME="SHiFTCodeRedeemer",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

db_conn = database_controller.create_connection()


router = APIRouter()


@router.post(
    get_config().BASE_PATH + '/verify_gearbox',
    tags=["account"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def verify_gearbox(request: Request, gearboxData: GearboxFormData, config: AppConfig = Depends(get_config)):
    if gearboxData.gearbox_password:
        gearboxData.gearbox_password = encrypt(gearboxData.gearbox_password.encode(), config.ENCRYPTION_KEY.encode())
    else:
        raise Exception(f"User {gearboxData.gearbox_email} details could not be parsed.")

    crawler = BorderlandsCrawler(user=gearboxData.dict())
    try:
        logged_in_borderlands = crawler.login_gearbox()
        crawler.tear_down()

        if logged_in_borderlands:
            return True
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=e)

    return False


@router.post(
    get_config().BASE_PATH + '/register',
    tags=["account"],
    responses={
        422: {"model": ErrorResponse},
    }
)
async def register(request: Request, formData: UserFormData, config: AppConfig = Depends(get_config)):
    # Query database
    try:
        # if formData.password:
        #     formData.password = encrypt(formData.password.encode(), config.ENCRYPTION_KEY.encode())
        # if formData.gearbox_password:
        #     formData.gearbox_password = encrypt(formData.gearbox_password.encode(), config.ENCRYPTION_KEY.encode())

        # if not formData.password and not formData.gearbox_password:
        #     raise Exception(f"User {formData.email} details could not be parsed.")

        # user_id = database_controller.create_user(db_conn, formData.dict())
        # if not user_id:
        #     raise Exception(f"Could not create user {formData.email}")

        await request_email_confirmation(formData.email)

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail='Error')

    # return user_id


async def request_email_confirmation(email: str) -> None:
    token = hashlib.sha256(genword(length=256).encode()).hexdigest()
    uuid = generate_uuid()

    try:
        database_controller.create_user_confirmation(db_conn, uuid, email, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return await send_confirmation_email(email, token)


async def send_confirmation_email(email: str, token: str) -> None:
    subject = "Verify your SHiFT Redeemer account"
    msg = f"""Welcome to <a href="{get_config().SITE_URL}">SHiFT Code Redeemer</a>!<br/>
        <br/>
        <a href="{get_config().SITE_URL}/verify?token={token}">Click here</a>
        to verify your email and complete your sign up process.<br/>
        <br/>
        Thank you for joining!<br/>
    """

    # send email using fastmail
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        html=msg
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return True


@router.post(
    get_config().BASE_PATH + '/confirm',
    tags=["account"]
)
async def confirm_email(request: Request, token: str = token_query):
    # Validate inputs
    valid_params = {"token"}
    request_params = set(request.query_params.keys())
    bad_params = request_params - valid_params
    if bad_params:
        raise InvalidParameterError(request=request, params=bad_params)

    try:
        # set email confirmation in db by adding email and token to new table.
        uc = database_controller.get_email_confirmation_by_token(db_conn, token)
        if uc:
            user = database_controller.select_user_by_email(db_conn, uc['email'])  # make sure user exists

            if user:
                database_controller.verify_user(db_conn, user['_id'])  # set user to be verified.
                # remove any rows from user_confirmation taale with email (multiple verification emails sent)
                database_controller.delete_user_confimation_by_email(db_conn,
                                                                     user['email'])
    except Exception:
        raise HTTPException(status_code=500, detail='Error verifying user.')

    return user['email']
