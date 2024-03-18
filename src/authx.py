from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.results import InsertOneResult
from pymongo.errors import DuplicateKeyError

from config import Config, getDB, logs
from db.models import StatusModel

from routes.app import authRouter as app_router
from routes.entity import authRouter as entity_router
from db.models.app_model import AppModel


@asynccontextmanager
async def lifespan(api: FastAPI):
    identi_app_name = "No Identi APP"

    db:MongoClient = await getDB()
    db_server_info = db.server_info()['version']

    authx_apps = db[Config.AUTHX_DB][Config.APPS_DB]
    identi_app = authx_apps.find_one({"uuid": Config.IDENTI_APP_ID})

    if identi_app is None:
        try:
            new_identi_app: AppModel = AppModel(
                uuid=Config.IDENTI_APP_ID, 
                app_name="Identi AUTHX",
                parent_app_id=Config.IDENTI_APP_ID,
                parent_entity_id=Config.IDENTI_ENTITY_ID,
                entity_id=Config.IDENTI_ENTITY_ID,
                tenant=Config.IDENTI_ENTITY_ID,
                api_key=Config.IDENTI_API_KEY,
                disabled=False,
                roles=["admin", "manager"],
                scopes=["identi:apps:admin", "identi:apps:list", "identi:apps:create", "identi:apps:update", "identi:apps:delete"],
            )

            new_identi_app_json = new_identi_app.model_dump()
            new_identi_app_json["_id"] = new_identi_app_json["uuid"]

            inserted_identi_app:InsertOneResult = authx_apps.insert_one(new_identi_app_json)
            identi_app = authx_apps.find_one({"_id": inserted_identi_app.inserted_id})
        except DuplicateKeyError as e:
            logs.debug(f"Existing Identi APP [{e}]")
            identi_app = authx_apps.find_one({"_id": Config.IDENTI_APP_ID})
        except Exception as e:
            logs.error(f"Error creating Identi APP [{e}]")
            raise e

    identi_app_name = identi_app["app_name"]
    identi_app_id = identi_app["_id"]
    
    status = {
        "db": db_server_info, 
        "host": Config.API_HOST, 
        "version": Config.API_VERSION, 
        "identi_app": {
            "name": identi_app_name, 
            "id": identi_app_id,
        }
    }

    logs.info(f"Startup API [{status}]")
    yield
    logs.info(f"Shutdown API [{status}]")
    
    if db is not None: 
        db.close()

api = FastAPI(
    title="Authx Microservice",
    description="Authx by Identi",
    version=Config.API_VERSION,
    docs_url="/api-doc",
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
]
origins += Config.CORS_ORIGINS.split(",")

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/")
async def index():
    """
    Root Endpoint for Microservice
    """
    logs.debug("Root Endpoint Call")
    return f"Authx Microservice - {Config.API_VERSION}"


@api.get("/health", response_model=StatusModel)
async def health():
    """
    Status and Health Endpoint for Microservice
    """

    ok = StatusModel()
    ok.description = f"OK from HOST [{Config.API_HOST}]"
    logs.debug("Get Health Endpoint", ok)
    return ok

api.include_router(
    router=app_router,
)

api.include_router(
    router=entity_router,
)
