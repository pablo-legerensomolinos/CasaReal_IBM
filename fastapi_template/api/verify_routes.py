from fastapi import APIRouter, Request, Depends
from typing import Annotated

from fastapi_template.env import VerifyConfig
from fastapi_template.connectors.VerifyDecorator import VerifyValidator

import hashlib
import base64
import uuid
from urllib.parse import urlencode
import requests

verify_bp = APIRouter(prefix='/api/verify', tags=['IBM Verify'])


def create_code_challenge(verifier: str):
    verifier_bytes = verifier.encode('ascii')
    code_challenge = hashlib.sha256(verifier_bytes).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).rstrip(b'=')
    return code_challenge.decode('ascii')

# endpoint to get codeVerifier and code for the /auth body


@verify_bp.get('/login')
def login():
    # Example:
    # url: str = "https://phoenixspgi.verify.ibm.com/v1.0/endpoint/default/authorize"
    url: str = f"{VerifyConfig.service_url}/authorize"
    code_verifier = str(uuid.uuid4())
    code_challenge = create_code_challenge(code_verifier)
    querystring = {
        "client_id": VerifyConfig.client_id,
        "client_secret": VerifyConfig.login_secret,
        "redirect_uri": VerifyConfig.redirect_url,
        "scope": "openid email profile",
        "response_type": 'code',
        "code_challenge": code_challenge
    }
    print({"url": url+"?"+urlencode(querystring), "codeChallenge": code_challenge})
    return {"url": url+"?"+urlencode(querystring), "codeChallenge": code_challenge}

# endpoint to get accessToken to add as Authorization Bearer header in your securized endpoints


@verify_bp.post('/auth')
async def auth(request: Request):
    body = await request.json()   
    code = body['code']
    code_challenge = body['codeVerifier']

    # Example:
    # url: str = "https://phoenixspgi.verify.ibm.com/v1.0/endpoint/default/token"
    url = f"{VerifyConfig.service_url}/token"

    payload = {
        "code": code,
        "code_verifier": code_challenge,
        "grant_type": 'authorization_code',
        "redirect_uri": VerifyConfig.redirect_url,
        'authorization_code': 'code_verifier',
    }
    auth_data = (VerifyConfig.client_id + ':' +
                 VerifyConfig.login_secret).encode('ascii')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(auth_data).decode('ascii')}"
    }

    response: requests.Response = requests.request(
        "POST", url, data=urlencode(payload), headers=headers)

    response_body = response.json()
    return {'idToken': response_body['id_token'], 'accessToken': response_body['access_token']}

# Use example


@verify_bp.get('/example', summary="verify example endpoint")
def example(token: Annotated[str, Depends(VerifyValidator)]):
    return "Route correctly secured with verify"
