from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import LoginRequest, TokenOut, UserOut
from ..security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(user.email))

@router.get("/me", response_model=UserOut)
def me(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
