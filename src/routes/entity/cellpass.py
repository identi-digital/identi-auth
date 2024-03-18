from fastapi import HTTPException, status
from db.models.access_model import AccessModel
from services.mdb import getAccessEntity

from config import logs


async def authCellPass(cell: str, code: str, password: str) -> AccessModel:
    if cell == password or cell == code:

        logs.info("Cell and Password can't be the same")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cell and Password can't be the same",
            headers={"WWW-Authenticate": "Bearer"},
        )
    uuid = "123"
    entity: AccessModel = getAccessEntity(uuid)
    return entity
