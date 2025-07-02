import fastapi_template.env as env
from fastapi_template.Logger import Logger

from fastapi_template.connectors.CosClient import CosClient
from fastapi_template.connectors.DbManager import DatabaseManager
from fastapi_template.connectors.ElasticSearch import ElasticSearchClient
from fastapi_template.connectors.S3Client import S3Client
from fastapi_template.connectors.WatsonxClient import WatsonxClient, WatsonxAPIClient
from fastapi_template.connectors.WebSocketManager import WebSocketManager
from fastapi_template.connectors.MilvusClient import MilvusClient

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
