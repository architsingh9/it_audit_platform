import os, time
import bcrypt
from jose import jwt

JWT_SECRET = os.getenv("SECRET_KEY", "dev-secret")
JWT_ALG = "HS256"
JWT_TTL_SECONDS = 60 * 60 * 8  # 8 hours

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(sub: str) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + JWT_TTL_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
