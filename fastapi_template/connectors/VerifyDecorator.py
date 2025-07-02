import requests
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_template.env import VerifyConfig


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class VerifyValidator:
    def __init__(self, token: Annotated[str, Depends(oauth2_scheme)]):
        # Example:
        # url: str = "https://phoenixspgi.verify.ibm.com/v1.0/endpoint/default/introspect"
        url: str = f'{VerifyConfig.service_url}/introspect'
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        querystring = {
            "token": token,
            "token_type_hint": "access_token",
            "client_id": VerifyConfig.client_id,
            "client_secret": VerifyConfig.login_secret,
        }
        resp = requests.post(url, headers=headers, params=querystring)
        if(resp.json().get('active') == False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid or expired bearer token'
            )