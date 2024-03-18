from typing import List

from pymongo import MongoClient
from db.models import AccessModel, AppModel, AppRegister, EntityModel
from services.jwt import gen_apikey
from uuid import uuid4

from config import Config, getDB, logs


async def validateAppID(app_id: str, api_key: str) -> bool:
    db: MongoClient = await getDB()

    authx_apps = db[Config.AUTHX_DB][Config.APPS_DB]
    identi_app = authx_apps.find_one({'uuid': app_id, 'api_key': api_key})
    if not identi_app or identi_app["disabled"]:
        return False
    else:
        return identi_app


def getAccessAppByClient(
    entity_id: str, client_id: str, client_secret: str
) -> AccessModel:
    uuid = f"{client_id}-{client_secret}"
    entity: AccessModel = getAccessApp(uuid)

    logs.debug("Entity", entity)
    return entity


def getAccessApp(uuid: str) -> AccessModel:
    app: AppRegister = getRegisteredApp(uuid)
    entity: AccessModel = AccessModel(app)

    logs.debug("Entity", entity)
    return entity


def newRegisteredApp(
    app_name: str,
    app_source: str,
    tenant: str,
    did: str,
    expires: int,
    redirect_url: str,
    scopes: List[str],
    disabled: bool,
    app_reg_id: str,
    entity_reg_id: str,
) -> AppModel:
    new_app: AppModel = AppModel(
        uuid=str(uuid4()),
        app_name=app_name,
        app_source=app_source,
        tenant=tenant,
        did=did,
        exp=expires,
        redirect_url=redirect_url,
        scopes=scopes,
        disabled=disabled,
        client_id=gen_apikey(),
        client_secret=gen_apikey(),
        app_reg_id=app_reg_id,
        entity_reg_id=entity_reg_id,
    )

    logs.debug("App Entity", new_app)
    return new_app


def getRegisteredApp(app_id: str) -> AppRegister:
    registered_app: AppRegister = AppRegister(
        uuid=app_id,
        app_name="App Demo",
        app_source="https://github.com",
        tenant="0ded9033-cb5e-47cc-95a3-33837425b5d2",
        redirect_url="",
        scopes=["itpanel:rw"],
        disabled=False,
        exp=30,
    )

    logs.debug("App Entity", registered_app)
    return registered_app


def getAccessEntity(uuid: str) -> AccessModel:
    entity = AccessModel(
        uuid=uuid,
        did="0x0Ed4bD6b0E1b756dc7d49D5b335E79f33ACAd444",
        tenant="0x0Ed4bD6b0E1b756dc7d49D5b335E79f33ACAd444",
        country="CL",
        disabled=False,
        roles=getRoles(uuid=uuid),
    )

    logs.debug("Entity", entity)
    return entity


def getEntity(uuid: str) -> EntityModel:
    entity = EntityModel(
        uuid=uuid,
        did="0x0Ed4bD6b0E1b756dc7d49D5b335E79f33ACAd444",
        username="demo",
        dni="00009999",
        country="CL",
        first_name="Demo",
        last_name="Mock",
        wsp_number="00000000",
        cell_number="00000000",
        sms_number="00000000",
        email="no-email@no-domain.tld",
        disabled=False,
        roles=getRoles(uuid=uuid),
    )

    return entity


def getRoles(uuid: str) -> list[str]:
    roles = [
        "suite:read",
        "org:readwrite",
    ]
    return roles
