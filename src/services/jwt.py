import secrets
from fastapi import HTTPException, Header, Path, Security, status
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from config import Config, logs
from db.models import TokenModel
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader

api_key_query = APIKeyQuery(name=Config.API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=Config.API_KEY_NAME, auto_error=False)

app_id_query = APIKeyQuery(name="app-id", auto_error=False)
app_id_header = APIKeyHeader(name="app-id", auto_error=False)

client_id_query = APIKeyQuery(name="client-id", auto_error=False)
client_id_header = APIKeyHeader(name="client-id", auto_error=False)

client_secret_query = APIKeyQuery(name="client-secret", auto_error=False)
client_secret_header = APIKeyHeader(name="client-secret", auto_error=False)


def encode_token(
    data: dict,
    token_type: str = "entity",
    expires: int = Config.JWT_EXP,
    token_key:str =Config.JWT_SECRET,
    base_token: str = None,
) -> TokenModel:
    now = datetime.now(timezone.utc)
    expires_token = now + timedelta(seconds=expires)
    expires_refresh = now + timedelta(seconds=Config.JWT_REFRESH_EXP)
    data_encoded = data.copy()
    data_encoded.update({"exp": expires_token, "aud": token_type})
    data_encoded_refresh = {
        "uuid": data_encoded["uuid"],
        "did": data_encoded["did"],
        "tenant": data_encoded["tenant"],
        "disabled": data_encoded["disabled"],
        "exp": expires_refresh,
        "aud": f"{token_type}-refresh",
    }

    access_token = jwt.encode(
        claims=data_encoded,
        key=token_key,
        headers={"ori": "access"},
        algorithm=Config.JWT_ALG,
        access_token=base_token,
    )
    refresh_token = jwt.encode(
        claims=data_encoded_refresh,
        key=token_key,
        headers={"ori": "refresh"},
        algorithm=Config.JWT_ALG,
        access_token=base_token,
    )

    token = TokenModel(
        access_token=access_token,
        refresh_token=refresh_token,
        expires=expires,
    )

    return token


def decode_token(
    token: str,
    token_type: str = "entity",
    token_ori: str = "",
    verify_exp: bool = True,
    token_key:str =Config.JWT_SECRET,
    base_token: str = None,
) -> dict:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decoded = jwt.decode(
            token=token,
            key=token_key,
            audience=f"{token_type}{token_ori}",
            algorithms=Config.JWT_ALG,
            options={"verify_exp": verify_exp},
            access_token=base_token,
        )
        return decoded

    except ExpiredSignatureError as error:
        logs.error(f"Expired TOKEN: {error}")
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Expired TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as error:
        logs.error(f"Invalid TOKEN: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as error:
        logs.error(f"Error in TOKEN: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error in TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_app_expires(days: int = 1) -> int:
    # Convert Days to Seconds for use in JWT expires
    return 3600 * 24 * days


def gen_apikey() -> str:
    # Generate a KEY for use in API-KEY / API-SECRET and CLIENT-ID / CLIENT-SECRET
    return f"{secrets.token_urlsafe(4)}{secrets.token_urlsafe(6)}"


async def get_access_token_expired(access_token: str = Header()):
    decoded = decode_token(access_token, token_type="app", verify_exp=False)
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ACCESS TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_access_token(access_token: str = Header()):
    decoded = decode_token(access_token, token_type="app")
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ACCESS TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_refresh_token(refresh_token: str = Header()):
    base_token = get_access_token_expired()
    decoded = decode_token(
        refresh_token, token_type="app", token_ori="-refresh", base_token=base_token
    )
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid REFRESH TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_entity_token_expired(
    entity_token: str = Header(), access_token: str = Header()
):
    decoded = decode_token(
        entity_token, token_type="entity", verify_exp=False, base_token=access_token
    )
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ENTITY TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_entity_token(entity_token: str = Header(), access_token: str = Header()):
    decoded = decode_token(entity_token, token_type="entity", base_token=access_token)
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ENTITY TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_entity_refresh_token(
    refresh_token: str = Header(), access_token: str = Header()
):
    decoded = decode_token(
        refresh_token,
        token_type="entity",
        token_ori="-refresh",
        base_token=access_token,
    )
    if (not decoded.__contains__("disabled")) or bool(decoded["disabled"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ENTITY REFRESH TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


async def get_app_id_path(app_id: str = Path()):
    if app_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid APP ID",
        )

    return app_id


async def get_entity_id_path(entity_id: str = Path()):
    if entity_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Entity ID",
        )

    return entity_id


async def get_api_key(
    app_id_header: str = Header(alias="app_id"),
    api_key_header: str = Header(alias="api_key"),
) -> list[str, str]:
    if api_key_header and app_id_header:
        return {
            "app_id": app_id_header,
            "api_key": api_key_header,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must include API-KEY and APP-ID",
        )


async def get_client_id(
    client_id_query: str = Security(client_id_query),
    client_id_header: str = Security(client_id_header),
):
    if client_id_query:
        return client_id_query
    elif client_id_header:
        return client_id_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid client-id",
        )


async def get_client_secret(
    client_secret_query: str = Security(client_secret_query),
    client_secret_header: str = Security(client_secret_header),
):
    if client_secret_query:
        return client_secret_query
    elif client_secret_header:
        return client_secret_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid client-secret",
        )
