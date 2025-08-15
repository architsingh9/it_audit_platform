# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import EmailStr
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import User
from ..schemas import UserOut, TokenOut
from ..security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenOut)
async def login(request: Request, db: Session = Depends(SessionLocal)):
    """
    Accepts either:
      - JSON: {"email": "...", "password": "..."}
      - or Form: email=...&password=...
    We parse manually to avoid 422 validation traps.
    """
    data = {}
    ctype = request.headers.get("content-type", "")
    try:
        if ctype.startswith("application/json"):
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form)
    except Exception:
        pass

    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="email and password are required")

    # Optional: validate email shape quickly
    try:
        EmailStr(email)
    except Exception:
        raise HTTPException(status_code=422, detail="invalid email format")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return TokenOut(access_token=token)

@router.get("/me", response_model=UserOut)
def me(email: str, db: Session = Depends(SessionLocal)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
