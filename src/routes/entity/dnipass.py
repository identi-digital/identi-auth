from fastapi import HTTPException, status
from db.models.access_model import AccessModel
from services.mdb import getAccessEntity

from config import logs

async def authDNIPass(dni: str, password: str) -> AccessModel:
    if dni == password:

        logs.info("DNI and Password can't be the same")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI and Password can't be the same",
            headers={"WWW-Authenticate": "Bearer"},
        )
    uuid = "123"
    entity: AccessModel = getAccessEntity(uuid)
    return entity
