from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User
from .security import parse_bearer_token, decode_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(parse_bearer_token), db: Session = Depends(get_db)) -> User:
    email = decode_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive user")
    return user
