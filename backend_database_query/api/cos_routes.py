from fastapi import APIRouter, Path
from fastapi.responses import PlainTextResponse
from typing import Annotated

from backend_database_query.Logger import Logger
from backend_database_query.connectors.CosClient import CosClient
from backend_database_query.env import CosConfig


logger = Logger("api_logger").logger

cos_bp = APIRouter(prefix='/api/cos', tags=['COS Operations'])


@cos_bp.get('/getBucket', summary="Retrieve bucket list from COS")
def cos_test():
    # COS client established
    cos_client = CosClient(CosConfig)
    
    result = cos_client.get_buckets()
    return result

@cos_bp.get('/getTextFile/{name}', summary="Retrieve text file  from COS")
def cos_test(name: Annotated[str, Path(title="Name of the text file to fetch")]):
    # COS client established
    cos_client = CosClient(CosConfig)
    
    result = cos_client.get_object(name)
    return PlainTextResponse(content=result['data'], media_type=result['ContentType'])

