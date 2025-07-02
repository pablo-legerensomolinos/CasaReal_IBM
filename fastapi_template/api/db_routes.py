from fastapi import APIRouter

from fastapi_template.Logger import Logger
from fastapi_template.connectors.DbManager import DatabaseManager
from fastapi_template.env import Db2Config

from fastapi_template.models.LastFilesModel import LastFilesAPI

logger = Logger("api_logger").logger
db_bp = APIRouter(prefix='/api/db2', tags=['DB2'])


@db_bp.get(
    '/test',
    summary="Retrieve Data from DB2",
    description="Get data from DB2 with SQLAlchemy ORM"
)
def db_test() -> list[LastFilesAPI]:
    # DB manager stablished
    db_manager = DatabaseManager(Db2Config)
    result = db_manager.getLastFiles()
    return result
