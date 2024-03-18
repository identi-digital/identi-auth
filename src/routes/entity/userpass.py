from fastapi import HTTPException, status
from db.models.access_model import AccessModel
from services.mdb import getAccessEntity

from config import logs

async def authUserPass(username: str, password: str) -> AccessModel:
    if username == password:

        logs.info("Username and Password can't be the same")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and Password can't be the same",
            headers={"WWW-Authenticate": "Bearer"},
        )
    uuid = "123"
    entity: AccessModel = getAccessEntity(uuid)
    return entity
