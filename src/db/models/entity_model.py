from datetime import datetime
from .access_model import AccessModel


class EntityModel(AccessModel):
    username: str | None = None
    dni: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    wsp_number: str | None = None
    cell_number: str | None = None
    sms_number: str | None = None
    email: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
