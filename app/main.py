from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import get_config
from app.routes import codes, user_codes, user_games, login, account

tags_metadata = [
    {
        "name": "code",
        "description": "Query Borderland game codes",
    },
    {
        "name": "user_game",
        "description": "Query user set user_games for redeeming on specific platforms.",
    }
]

origins = [
    "http://localhost:8080",
    "http://localhost",
    "http://borderlands-angular-github-amazon-s3.s3-website.eu-west-2.amazonaws.com",
    "http://shift-code-tool-review.s3-website.eu-west-2.amazonaws.com",
    "http://shift-code-tool-develop.s3-website.eu-west-2.amazonaws.com",
    "http://shift-code-tool-production.s3-website.eu-west-2.amazonaws.com"
]


def get_app():
    config = get_config()

    # Create app
    app = FastAPI(
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        openapi_url=config.OPENAPI_URL,
        openapi_tags=tags_metadata)

    # Add CORS headers response from requests where Origin header is set
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(codes.router)
    app.include_router(user_codes.router)
    app.include_router(user_games.router)
    app.include_router(login.router)
    app.include_router(account.router)


    return app


app = get_app()


from mangum import Mangum
handler = Mangum(app)
