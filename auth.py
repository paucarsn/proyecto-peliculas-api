from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-solo-para-local")
SECRET_KEY = "$2b$12$KIXQ7jK9vXZ3n8oP2mF5aOxYzT1wRcVbNjLkMqHfDsEg6hIj7kLmO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password:str):
    return pwd_context.hash(password)

def verificar_password(password:str, hashed_password:str):
    return pwd_context.verify(password, hashed_password)

def crear_token(data:dict):
    to_encode = data.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalido")
        return username
    except JWError:
        raise HTTPException(status_code=401, detial="Token Invalido")

