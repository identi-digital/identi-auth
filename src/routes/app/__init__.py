from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Form, HTTPException, Header, Security, status
from pymongo import MongoClient
from pymongo.results import InsertOneResult

from db.models import AppRegister, AppModel, TokenModel
from services.jwt import (
    decode_token,
    encode_token,
    gen_apikey,
    get_api_key,
)
from config import Config, getDB, logs
from services.mdb import validateAppID

authRouter = APIRouter(
    prefix="/app",
    tags=["APP-Auth"],
    dependencies=[
        Security(get_api_key, use_cache=False),
    ],
)


@authRouter.post("/register", response_model=AppModel)
async def register(
    new_app: AppRegister = Annotated[AppRegister, Form()],
    app_api_header: str = Security(get_api_key, use_cache=False),
):
    valApp = await validateAppID(
        app_id=app_api_header["app_id"],
        api_key=app_api_header["api_key"],
    )

    if not valApp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API-KEY and APP-ID",
        )
    logs.info(f"Creating new APP [{new_app.app_name}]")

    created_app: AppModel = AppModel.model_validate(new_app)
    created_app.parent_app_id = valApp["uuid"]
    created_app.parent_entity_id = valApp["entity_id"]
    created_app.uuid = uuid4().__str__()
    created_app.entity_id = uuid4().__str__()
    created_app.api_key = gen_apikey()

    new_identi_app_json = created_app.model_dump()
    new_identi_app_json["_id"] = new_identi_app_json["uuid"]

    db:MongoClient = await getDB()
    authx_apps = db[Config.AUTHX_DB][Config.APPS_DB]    
    inserted_identi_app:InsertOneResult = authx_apps.insert_one(new_identi_app_json)

    logs.info(f"Created new APP [{inserted_identi_app.inserted_id}]")

    return new_identi_app_json

@authRouter.post("/token", response_model=TokenModel)
async def token(
    app_api_header: str = Security(get_api_key, use_cache=False),
):
    valApp = await validateAppID(
        app_id=app_api_header["app_id"],
        api_key=app_api_header["api_key"],
    )

    if not valApp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API-KEY and APP-ID",
        )
    
    app: AppModel = AppModel.model_validate(valApp)
    
    logs.info(f"Generating TOKEN for APP [{app.uuid}]")

    app_token = {
        "uuid": app.uuid,
        "did": app.did,
        "tenant": app.tenant,
        "disabled": app.disabled,
        "country": app.country,
        "created_at": str(app.created_at),
    }
    token_key = f"{app.entity_id}:{app.api_key}"

    return encode_token(data=app_token, expires=app.exp, token_type="app", base_token=Config.APP_ACCESS_TOKEN, token_key=token_key)

@authRouter.get("/validate", response_model=AppRegister)
async def validate(
    app_api_header: str = Security(get_api_key, use_cache=False),
    access_token: str = Header(alias="access_token"),
):
    valApp = await validateAppID(
        app_id=app_api_header["app_id"],
        api_key=app_api_header["api_key"],
    )

    if not valApp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API-KEY and APP-ID",
        )
    
    app: AppModel = AppModel.model_validate(valApp)
    token_key = f"{app.entity_id}:{app.api_key}"
    app_token = decode_token(token=access_token, token_type="app", base_token=Config.APP_ACCESS_TOKEN, token_key=token_key)

    app_id = app_token["uuid"]

    logs.info(f"Validating TOKEN for APP [{app_id}]")
    
    app:AppRegister = AppRegister.model_dump(app)

    return app

@authRouter.get("/refresh", response_model=TokenModel)
async def refresh(
    app_api_header: str = Security(get_api_key, use_cache=False),
    refresh_token: str = Header(alias="refresh_token"),
):
    valApp = await validateAppID(
        app_id=app_api_header["app_id"],
        api_key=app_api_header["api_key"],
    )

    if not valApp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API-KEY and APP-ID",
        )
    
    app: AppModel = AppModel.model_validate(valApp)
    token_key = f"{app.entity_id}:{app.api_key}"
    decoded_token = decode_token(verify_exp=False, token=refresh_token, token_type="app", base_token=Config.APP_ACCESS_TOKEN, token_key=token_key)

    app_id = decoded_token["uuid"]

    logs.info(f"Refreshing TOKEN for APP [{app_id}]")

    app_token = {
        "uuid": app.uuid,
        "did": app.did,
        "tenant": app.tenant,
        "disabled": app.disabled,
        "country": app.country,
        "created_at": str(app.created_at),
    }
    token_key = f"{app.entity_id}:{app.api_key}"

    return encode_token(data=app_token, expires=app.exp, token_type="app", base_token=Config.APP_ACCESS_TOKEN, token_key=token_key)
