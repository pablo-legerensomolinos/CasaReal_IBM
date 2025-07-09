from os import environ
from dotenv import dotenv_values

config_env = {
    **dotenv_values('.env'),
    **dotenv_values('.env.pre'),  # override prod envs with pre-production
    **dotenv_values(".env.dev"),  # override prod envs with development
    **dotenv_values('.env.secret'),  # doesn't break if missing
    **environ,  # Override all with command-line defined envs
}


class ServerConfig:
    env = config_env.get('ENV', 'dev')
    host = config_env.get('API_HOST', '0.0.0.0')
    port = int(config_env.get('API_PORT', 8000))
    # set the url for the openapi to the code engine one or
    # if not detected to the manually set `SERVER_URL`
    # otherwise fallback to localhost
    # TODO: when needed add here the openshift variant
    url = (f'https://{config_env.get("CE_APP")}.'
           f'{config_env.get("CE_SUBDOMAIN")}.'
           f'{"private." if config_env.get("PRIVATE_ENDPOINT") != None else ""}'
           f'{config_env.get("CE_DOMAIN")}') if config_env.get("CE_APP") != None else config_env.get("SERVER_URL", "http://localhost:8000")


class ElasticConfig:
    url = config_env.get("ELASTIC_URL")
    user = config_env.get("ELASTIC_USER")
    passwd = config_env.get("ELASTIC_PASSWD")
    cert_path = config_env.get("ELASTIC_CERT_PATH")
    index = config_env.get("ELASTIC_INDEX")


class MilvusConfig:
    uri = config_env.get("MILVUS_URI")
    user = config_env.get("MILVUS_USER")
    password = config_env.get("MILVUS_PASSWORD")
    db_name = config_env.get("MILVUS_DB_NAME", "default")


class Db2Config:
    password = config_env.get("DB_PASSWORD")
    username = config_env.get("DB_USERNAME")
    hostname = config_env.get("DB_HOSTNAME")
    port = config_env.get("DB_PORT")
    database = config_env.get("DB_DATABASE")
    schema = config_env.get("DB_SCHEMA")
    security = config_env.get("DB_SECURITY")
    ssl_server_certificate = config_env.get("DB_SSL_SERVER_CERTIFICATE")


class WatsonxAPIConfig:
    def __init__(self):
        self.apikey = config_env.get("WATSONX_AI_APIKEY")
        self.url = config_env.get("WATSONX_AI_HOST")
        self.project_id = config_env.get("WATSONX_AI_PROJECT_ID")
        self.space_id = config_env.get("WATSONX_AI_SPACE_ID")
        self.limits = int(config_env.get('WATSONX_AI_LIMITS', 50))


class WatsonxConfig(WatsonxAPIConfig):
    def __init__(self, deployment_id=None, model_id=None):
        super().__init__()  # <-- This initializes url, apikey, etc.
        self.deployment_id = deployment_id or config_env.get("WATSONX_AI_DEPLOYMENT_ID")
        self.model_id = model_id or config_env.get("WATSONX_MODEL_ID", None)

WATSONX_AI_DEPLOYMENT_INTERPRETATION_ID = config_env.get("WATSONX_AI_DEPLOYMENT_INTERPRETATION_ID")  # Default model for interpretation

class WatsonxSampleInheritanceSample(WatsonxConfig):
    # sample on how to use inheritance on the envs to not having to duplicate envs
    deployment_id = config_env.get("WATSONX_AI_OVERRIDE_ENV")


class EmbeddingsConfig(WatsonxConfig):
    dense_embedding_id = config_env.get("DENSE_EMBEDDING_MODEL_ID")


class VerifyConfig:
    client_id = config_env.get("VERIFY_LOGIN_CLIENT_ID")
    login_secret = config_env.get("VERIFY_LOGIN_SECRET")
    service_url = config_env.get("VERIFY_LOGIN_SERVICE_URL")
    redirect_url = config_env.get("VERIFY_LOGIN_REDIRECT_URL")


class HttpBasicAuthConfig:
    username = config_env.get("HTTP_BASIC_AUTH_USERNAME")
    password = config_env.get("HTTP_BASIC_AUTH_PASSWORD")


class CosConfig:
    api_key = config_env.get("COS_API_KEY")
    service_instance_id = config_env.get("COS_INSTANCE_CRN")
    endpoint_url = config_env.get("COS_ENDPOINT")
    bucket = config_env.get("COS_BUCKET")


class S3Config:
    hmac_access_key_id = config_env.get("S3_HMAC_ACCESS_KEY_ID")
    hmac_secret_access_key = config_env.get("S3_HMAC_SECRET_ACCESS_KEY")
    endpoint_url = config_env.get("S3_ENDPOINT")
    bucket = config_env.get("S3_BUCKET")


class LogConfig:
    misc_level = config_env.get("LOG_MISC", "ERROR")


class WDConfig:
    wd_version = config_env.get("WD_VERSION")
    wd_url = config_env.get("WD_URL")
    wd_project_id = config_env.get("WD_PROJECT_ID")
    wd_collection_id = config_env.get("WD_COLLECTION_ID")
    wd_apikey = config_env.get("WD_APIKEY")
