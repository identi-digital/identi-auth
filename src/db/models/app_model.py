from datetime import datetime
from .access_model import AccessModel


class AppRegister(AccessModel):
    app_name: str = "new app"
    app_source: str = "no-source"
    redirect_url: str | None = None


class AppModel(AppRegister):
    uuid: str | None = None
    did: str | None = None
    parent_app_id: str = "parent identi app id"
    parent_entity_id: str = "parent identi entity id"
    entity_id: str = "identi entity id"
    api_key: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
