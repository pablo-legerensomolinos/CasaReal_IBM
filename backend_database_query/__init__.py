from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import requests
# import instana


from .Logger import Logger
from .env import ServerConfig
# from .api.db_routes import db_bp
from .api.watsonx_routes import watsonx_bp
# from .api.elastic_routes import elastic_bp
# from .api.verify_routes import verify_bp
# from .api.httpAuth_routes import http_auth
# from .api.cos_routes import cos_bp
# from .api.s3_routes import s3_bp
# from .api.websocket_routes import ws_bp

from .business_logic.clients_initialitation import clients_initialitation


def create_app():
    # Set up the OpenAPI app
    app = FastAPI(
        title=__name__,
        description="Backend Project API",
        version="1.0.0",
        servers=[
            {"url": ServerConfig.url}
        ],
    )

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pre-start the clients
    # clients_initialitation()

    # Register the blueprints
    # app.include_router(db_bp)
    app.include_router(watsonx_bp)
    # app.include_router(elastic_bp)
    # app.include_router(verify_bp)
    # app.include_router(cos_bp)
    # app.include_router(s3_bp)
    # app.include_router(ws_bp)
    # app.include_router(http_auth)

    # Health Api
    @app.get(
        "/health",
        summary="Health check",
        description="Endpoint for probbing the application",
        tags=['OCP']
    )
    def health():
        return {"Status": "OK!"}

    return app


app = create_app()


def start(reload: bool = False):
    """Launched with `poetry run start` at root level"""
    uvicorn.run("backend_database_query:app", host="0.0.0.0", port=8000, reload=reload)


def start_dev():
    start(reload=True)
