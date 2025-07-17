from fastapi import APIRouter

from backend_database_query.Logger import Logger
from backend_database_query.connectors.DbManager import DatabaseManager
from backend_database_query.env import Db2Config

from backend_database_query.models.LastFilesModel import LastFilesAPI

logger = Logger("api_logger").logger
db_bp = APIRouter(prefix='/api/db2', tags=['DB2'])


@db_bp.get(
    '/test',
    summary="Retrieve Data from DB2",
    description="Get data from DB2 with SQLAlchemy ORM"
)
def db_test():
    # DB manager stablished
    db_manager = DatabaseManager(Db2Config())
    result = db_manager.test_connection()
    return result

@db_bp.get(
    '/ex_query',
    summary="Test DB2 Connection",
    description="Get current date from DB2"
)
def db_exQuery():
    db_manager = DatabaseManager(Db2Config())
    result = db_manager.execute_sql('SELECT * FROM articles')
    return result
