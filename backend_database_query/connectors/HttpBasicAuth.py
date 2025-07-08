import  secrets
from    fastapi             import Depends, HTTPException, status
from    fastapi.security    import HTTPBasic, HTTPBasicCredentials

class HttpBasicAuth:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.security = HTTPBasic()

    def check_http_authentication(self, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
        if credentials is None:
            raise HTTPException(status_code=400, detail="Missing credentials")

        correct_username = secrets.compare_digest(credentials.username, self.username)
        correct_password = secrets.compare_digest(credentials.password, self.password)

        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username