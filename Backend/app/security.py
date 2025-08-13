from datetime import datetime
from jose import jwt, JWTError
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Header
from typing import Optional
from .config import SECRET_KEY, ALGORITHM, JWT_EXPIRE_DELTA

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    payload = {"sub": subject, "exp": datetime.utcnow() + JWT_EXPIRE_DELTA}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def parse_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return authorization.split(" ", 1)[1]
