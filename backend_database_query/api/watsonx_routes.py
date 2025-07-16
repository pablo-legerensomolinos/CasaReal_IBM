from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend_database_query.Logger import Logger
from backend_database_query.connectors.WatsonxClient import WatsonxClient
from backend_database_query.env import WatsonxConfig, WatsonxAPIConfig
from backend_database_query.business_logic.nl_to_sql import process_nl_query

logger = Logger("api_logger").logger
watsonx_bp = APIRouter(prefix='/api/wx', tags=["watsonX.ai"])

class Request(BaseModel):
    question: str


@watsonx_bp.get('/test', summary="Test IBM Watsonx AI Connection")
def wxai_test():
    wx_config = WatsonxConfig()
    wx_apiconfig = WatsonxAPIConfig()
    wx_client = WatsonxClient(wx_config, wx_apiconfig)
    list_models = wx_client.list_models()
    #tokenize = wx_client.tokenize("tokenize this phrase")
    return {"list_models": list_models} #, "tokenize": tokenize}

@watsonx_bp.post('/query', summary="Procesar consulta en lenguaje natural")
def wxai_nl_to_sql(request: Request):
    """
    Recibe una consulta en lenguaje natural, la traduce a SQL, ejecuta la consulta y devuelve la respuesta interpretada.
    """
    try:
        body = request.json()
        question = body.get("question")

        if not question:
            raise HTTPException(status_code=400, detail="Missing 'question' in request body.")

        response = process_nl_query(question)
        return {"response": response}

    except Exception as e:
        logger.error(f"Error procesando la consulta: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al procesar la consulta.{e}")
