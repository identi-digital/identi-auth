import logging
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from .version import API_VERSION

load_dotenv()

_log_level = logging.INFO
if os.getenv("DEBUG", "no") == "yes":
    _log_level = logging.DEBUG

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=_log_level
)

logs = logging.getLogger("IdentiAuthX")


class Config:
    API_VERSION = API_VERSION
    API_HOST = os.getenv("API_HOST", "no-hostname")
    APP_ACCESS_TOKEN = os.getenv("APP_ACCESS_TOKEN", "no-app-access-token")
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:9000"
    )

    JWT_SECRET = os.getenv("JWT_SECRET", "no-jwt-secret")
    JWT_ALG = os.getenv("JWT_ALG", "HS256")
    JWT_EXP = int(os.getenv("JWT_EXP", "60"))
    JWT_REFRESH_EXP = int(os.getenv("JWT_REFRESH_EXP", "120"))
    
    API_KEY_NAME = os.getenv("API_KEY_NAME", "no-api-key-name")
    API_KEY_AUTH = os.getenv("API_KEY_AUTH", "no-api-key-auth")

    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    AUTHX_DB = os.getenv("AUTHX_DB", "no-authx-db")
    APPS_DB = os.getenv("APPS_DB", "no-apps-db")
    ENTITIES_DB = os.getenv("ENTITIES_DB", "no-entities-db")

    IDENTI_API_KEY = os.getenv("IDENTI_API_KEY", "no-identi-api-key")
    IDENTI_APP_ID = os.getenv("IDENTI_APP_ID", "no-identi-app-id")
    IDENTI_ENTITY_ID = os.getenv("IDENTI_ENTITY_ID", "no-identi-entity-id")

_client: MongoClient = None

async def getDB()->MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGODB_URL)
    return _client