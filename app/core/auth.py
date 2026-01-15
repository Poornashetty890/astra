from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings
from app.models.device import Astra
from app.models.user import AstraUser

SECRET_KEY=get_settings().secret_key
ALGORITHM="HS256"
TOKEN_EXPIRE_IN_MINUTES=2400


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/foodie/v1/restaurant/login")

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data:dict, expire_minutes:Optional[int]=None):
    to_encode=data.copy()
    if expire_minutes:
        expires=datetime.now(tz=timezone.utc)+timedelta(minutes=expire_minutes)
        to_encode.update({"exp":expires})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return token

async def get_current_entity(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid Credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        entity_id = payload.get("sub")
        role = payload.get("role",None)
        if entity_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if role and role == "device":
        entity = await Astra.find_one(Astra.device_id == entity_id)
    else:
        entity = await AstraUser.find_one(AstraUser.user_id == entity_id)
    if entity is None:
        raise credentials_exception
    return entity
