from fastapi import FastAPI
from application.routes import router


def get_app():
    app = FastAPI()
    app.include_router(router)
    return app


app = get_app()
