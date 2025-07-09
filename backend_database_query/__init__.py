from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import requests
# import instana


from .Logger import Logger
from .env import ServerConfig
from .api.db_routes import db_bp
from .api.watsonx_routes import watsonx_bp
from .api.elastic_routes import elastic_bp
from .api.verify_routes import verify_bp
from .api.httpAuth_routes import http_auth
from .api.cos_routes import cos_bp
from .api.s3_routes import s3_bp
from .api.websocket_routes import ws_bp

from .business_logic.clients_initialitation import clients_initialitation


def create_app():
    # Set up the OpenAPI app
    app = FastAPI()

    origins = [
        "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pre-start the clients
    # clients_initialitation()

    # Register the blueprints
    app.include_router(db_bp)
    app.include_router(watsonx_bp)
    app.include_router(elastic_bp)
    app.include_router(verify_bp)
    app.include_router(cos_bp)
    app.include_router(s3_bp)
    app.include_router(ws_bp)
    app.include_router(http_auth)

    # Health Api
    @app.get(
        "/health",
        summary="Health check",
        description="Endpoint for probbing the application",
        tags=['OCP']
    )
    def health():
        return {"Status": "OK!"}

    # OpenAPI documentation route in /docs directly or through this
    # route to get it for the frontend in json format
    @app.get(
        '/api/docs',
        summary="OpenAPI in JSON format",
        description="Route that server the generated OpenAPI file in JSON format",
        tags=['OpenAPI']
    )
    def serveOpenapi():
        openapi_json = (requests.request(
            "GET", f"http://localhost:{ServerConfig.port}/openapi.json")).json()
        return openapi_json

    # Manually configure openapi doc
    openapi_schema = get_openapi(
        title=__name__,
        description="Backend Project API",
        version="1.0.0",
        servers=[
            {"url": ServerConfig.url}
        ],
        routes=app.routes,
        # check for latest possible version
        # https://www.ibm.com/docs/en/watsonx/watson-orchestrate/current?topic=skills-creating-openapi-specifications#configuring-the-openapi-version
        openapi_version="3.0.3"
    )
    openapi_schema['components'] = {
        **openapi_schema.get('components', {}),
        "securitySchemes": {
            "basic_auth": {
                "type": "http",
                "scheme": "basic"
            }
        }
    }
    openapi_schema['security'] = [
        {
            "Basic": []
        }
    ]

    # Find all parameters with anyOf and update them
    for path, path_item in openapi_schema["paths"].items():
        for method, method_item in path_item.items():
            parameters = method_item.get("parameters", [])
            for param in parameters:
                param_schema = param["schema"]
                if "anyOf" in param_schema:
                    param_type = param_schema["anyOf"][0]["type"]
                    param_schema["type"] = param_type
                    param_schema.pop("anyOf", None)
                    param_schema["nullable"] = True

    # Find all schemas ending with API and update their properties, e.g. EmpresaAPI
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    for _, schema in schemas.items():
        for prop in schema.get("properties", {}).values():
            if "anyOf" in prop:
                prop_type = prop["anyOf"][0].get("type", None)
                if prop_type == None:
                    prop_type = prop["anyOf"][0].get("$ref", None)
                prop["type"] = prop_type
                prop.pop("anyOf", None)
                prop["nullable"] = True

    if schemas.get('ValidationError', None):
        validationErrorAnyOf = schemas['ValidationError']['properties']['loc']['items']
        prop_type = validationErrorAnyOf["anyOf"][0]["type"]
        validationErrorAnyOf["type"] = prop_type
        validationErrorAnyOf.pop("anyOf", None)
        validationErrorAnyOf["nullable"] = True

    app.openapi_schema = openapi_schema

    return app


app = create_app()


def start(reload: bool = False):
    """Launched with `poetry run start` at root level"""
    uvicorn.run("backend_database_query:app", host="0.0.0.0",
                port=4010, reload=reload)


def start_dev():
    start(reload=True)
