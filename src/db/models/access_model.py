from pydantic import BaseModel


class AccessModel(BaseModel):
    class Config:
        from_attributes = True

    tenant: str
    country: str = "PE"
    disabled: bool = True
    exp: int = 1
    roles: list[str] = ["user"]
    scopes: list[str] = ["app", "app:create", "app:edit"]
