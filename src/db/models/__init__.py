from pydantic import BaseModel
from .app_model import AppModel, AppRegister  # noqa: F401
from .entity_model import EntityModel   # noqa: F401
from .access_model import AccessModel   # noqa: F401

class StatusModel(BaseModel):
    code: str = 'OK'
    description: str = 'OK from HOST [localhost]'


class BaseTokenModel(BaseModel):
    access_token: str
    refresh_token: str = ''


class TokenModel(BaseTokenModel):
    token_type: str = 'Bearer'
    expires: int = 1200
