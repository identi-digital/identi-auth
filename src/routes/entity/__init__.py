from fastapi import APIRouter, Depends, Form, HTTPException, Header, Security, status
from db.models import EntityModel, TokenModel
from db.models.access_model import AccessModel
from services.mdb import getAccessEntity, getEntity
from .userpass import authUserPass
from .dnipass import authDNIPass
from .cellpass import authCellPass
from services.jwt import (
    encode_token,
    get_access_token,
    get_entity_id_path,
    get_entity_refresh_token,
    get_entity_token,
    get_entity_token_expired,
)
from config import logs

authRouter = APIRouter(
    prefix="/entity",
    tags=["Entity-Auth"],
    dependencies=[Security(get_access_token, use_cache=False)],
)


@authRouter.post("/register")
async def register(
    username: str = Form(),
    password: str = Form(),
    dni: str = Form(),
    country: str = Form(),
    first_name: str = Form(),
    last_name: str = Form(),
    wsp_number: str = Form(),
    cell_number: str = Form(),
    sms_number: str = Form(),
    email: str = Form(),
    role: str = Form(default='read'),
    access_token: str = Header(),
) -> EntityModel:
    uuid = "234-234"
    entity = getEntity(uuid)

    logs.debug("Entity", entity)
    return entity


@authRouter.post("/userpass")
async def userPass(
    username: str = Form(),
    password: str = Form(),
    access_token: str = Header(),
) -> TokenModel:
    entity: AccessModel = await authUserPass(username, password)

    logs.debug("Entity", entity)
    return encode_token(entity, token_type="entity", base_token=access_token)


@authRouter.post("/dnipass")
async def dniPass(
    dni: str = Form(),
    password: str = Form(),
    access_token: str = Header(),
) -> TokenModel:
    entity: AccessModel = await authDNIPass(dni, password)

    logs.debug("Entity", entity)
    return encode_token(entity, token_type="entity", base_token=access_token)


@authRouter.post("/cellpass")
async def cellPass(
    cell: str = Form(),
    code: str = Form(),
    password: str = Form(),
    access_token: str = Header(),
) -> TokenModel:
    entity: AccessModel = await authCellPass(cell, code, password)

    logs.debug("Entity", entity)
    return encode_token(entity, token_type="entity", base_token=access_token)


@authRouter.get("/{entity_id}/validate", response_model=EntityModel)
async def validate(
    entity_id: str = Depends(get_entity_id_path),
    entity_token: str = Depends(get_entity_token, use_cache=False),
):
    if entity_token["uuid"] == entity_id:
        entity: EntityModel = getEntity(entity_id)

        logs.debug("Entity", entity)
        return entity
    else:

        logs.error("Bad Entity TOKEN")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bad TOKENS",
            headers={"WWW-Authenticate": "Bearer"},
        )


@authRouter.post("/{entity_id}/refresh", response_model=TokenModel)
async def refresh(
    entity_id: str = Depends(get_entity_id_path),
    entity_token: str = Depends(get_entity_token_expired, use_cache=False),
    refresh_token: str = Depends(get_entity_refresh_token, use_cache=False),
    access_token: str = Header(),
):
    if (
        entity_token["uuid"] == refresh_token["uuid"]
        and refresh_token["uuid"] == entity_id
    ):
        entity: AccessModel = getAccessEntity(entity_id)

        logs.debug("Entity", entity)
        return encode_token(entity, token_type="entity", base_token=access_token)
    else:

        logs.error("Bad Entity TOKEN")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bad TOKENS",
            headers={"WWW-Authenticate": "Bearer"},
        )
