from fastapi import APIRouter

from fastapi_template.Logger import Logger
from fastapi_template.connectors.WatsonxClient import WatsonxClient
from fastapi_template.env import WatsonxConfig

logger = Logger("api_logger").logger
watsonx_bp = APIRouter(prefix='/api/wx', tags=["watsonX.ai"])


@watsonx_bp.get('/test', summary="Test IBM Watsonx AI Connection")
def wxai_test():
    wx_client = WatsonxClient(WatsonxConfig)
    list_models = wx_client.list_models()
    tokenize = wx_client.tokenize("tokenize this phrase")
    return {"list_models": list_models, "tokenize": tokenize}
