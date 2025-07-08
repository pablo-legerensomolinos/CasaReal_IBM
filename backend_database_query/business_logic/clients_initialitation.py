import backend_database_query.env as env
from backend_database_query.Logger import Logger

from backend_database_query.connectors.CosClient import CosClient
from backend_database_query.connectors.DbManager import DatabaseManager
from backend_database_query.connectors.ElasticSearch import ElasticSearchClient
from backend_database_query.connectors.S3Client import S3Client
from backend_database_query.connectors.WatsonxClient import WatsonxClient, WatsonxAPIClient
from backend_database_query.connectors.WebSocketManager import WebSocketManager
from backend_database_query.connectors.MilvusClient import MilvusClient

logger = Logger('app_logger', env.LogConfig.misc_level).logger


def clients_initialitation():
    logger.info("Starting clients preemptively")
    CosClient(env.CosConfig)
    DatabaseManager(env.Db2Config)
    ElasticSearchClient(env.ElasticConfig)
    S3Client(env.S3Config)
    WatsonxAPIClient(env.WatsonxConfig)
    WatsonxClient(env.WatsonxConfig)
    WebSocketManager()
    MilvusClient(env.MilvusConfig, env.EmbeddingsConfig)

    logger.info("All clients started correctly")
