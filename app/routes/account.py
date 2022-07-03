import logging
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from app import database_controller
from app.config import get_config, AppConfig
from app.models.schemas import GearboxFormData, UserFormData, ErrorResponse
from app.borderlands_crawler import BorderlandsCrawler
from app.util import encrypt

database = "borderlands_codes.db"
db_conn = database_controller.create_connection(database)


router = APIRouter()


@router.post(
    get_config().BASE_PATH + '/verify_gearbox',
    tags=["account"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def verify_gearbox(request: Request, gearboxData: GearboxFormData, config: AppConfig = Depends(get_config)):
    gearboxData.gearbox_password = encrypt(gearboxData.gearbox_password.encode(), config.ENCRYPTION_KEY.encode())
    crawler = BorderlandsCrawler(user=gearboxData.dict())
    logged_in_borderlands = crawler.login_gearbox()
    crawler.tear_down()

    if logged_in_borderlands:
        return True
    return False


@router.post(
    get_config().BASE_PATH + '/register',
    tags=["account"],
    responses={
        422: {"model": ErrorResponse},
    }
)
def register(request: Request, formData: UserFormData, config: AppConfig = Depends(get_config)):
    # Query database
    try:
        if formData.password:
            formData.password = encrypt(formData.password.encode(), config.ENCRYPTION_KEY.encode())
        if formData.gearbox_password:
            formData.gearbox_password = encrypt(formData.gearbox_password.encode(), config.ENCRYPTION_KEY.encode())

        return database_controller.create_user(db_conn, formData.dict())
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Database error")
