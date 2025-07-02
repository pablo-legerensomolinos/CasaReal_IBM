from typing                                     import Annotated
from fastapi                                    import APIRouter, Depends, Request
from fastapi_template.Logger                    import Logger

from fastapi_template.env                       import HttpBasicAuthConfig
from fastapi_template.connectors.HttpBasicAuth  import HttpBasicAuth

logger       = Logger("api_logger").logger

http_auth    = APIRouter(prefix='/api/http_auth', tags=['HTTP Basic Auth'])
credentials  = HttpBasicAuth(HttpBasicAuthConfig.username, HttpBasicAuthConfig.password)


# Get Example
@http_auth.get('/get_example', summary = "Get Http Basic Auth example secured endpoint")
def get_example(username: Annotated[str, Depends(credentials.check_http_authentication)]):
    return {"message": f"Hello, {username}! You have access."}

@http_auth.post('/post_example', summary = "Post Http Basic Auth example secured endpoint")
async def post_example(request: Request, username: Annotated[str, Depends(credentials.check_http_authentication)]):
    body   = await request.json()
    return {"message": f"Hello, {username}! Your data are: {body}."}