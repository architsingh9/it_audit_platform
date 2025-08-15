from datetime import datetime
from jose import jwt, JWTError
from fastapi import HTTPException, status, Header
from typing import Optional
import bcrypt

from .config import SECRET_KEY, ALGORITHM, JWT_EXPIRE_DELTA


# --- Password hashing (bcrypt direct) ---

def hash_password(password: str) -> str:
    """Return a bcrypt hash (utf-8 string)."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash string."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# --- JWT helpers ---

def create_access_token(subject: str) -> str:
    payload = {"sub": subject, "exp": datetime.utcnow() + JWT_EXPIRE_DELTA}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def parse_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return authorization.split(" ", 1)[1]
