from pwdlib import PasswordHash
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jwt import encode, decode
from jwt.exceptions import PyJWKError, DecodeError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.database.config_db import get_db
from api.database.banco import UserDB
from http import HTTPStatus
from api.settings import Settings



pwd_context = PasswordHash.recommended()
settings = Settings()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})
    encode_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encode_jwt


def get_current_user(session: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/token"))):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.query(UserDB).filter(UserDB.email == username).first()

    if user is None:
        raise credentials_exception
    
    return user