from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config
from app.routes import codes, user_codes, user_games

tags_metadata = [
    {
        "name": "code",
        "description": "Query Borderland game codes",
    }
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(codes.router)
    app.include_router(user_codes.router)
    app.include_router(user_games.router)
    return app


app = get_app()
