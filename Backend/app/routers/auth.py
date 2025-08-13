from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import Base, engine, SessionLocal
from ..models import User, Control
from ..schemas import UserOut, TokenOut
from ..security import hash_password, verify_password, create_access_token
from ..config import ROLES, STATUS

router = APIRouter(prefix="/auth", tags=["Auth"])

# Create tables & seed on import (dev convenience)
Base.metadata.create_all(bind=engine)
db_seed = SessionLocal()
try:
    # Seed users if empty
    if db_seed.query(User).count() == 0:
        demo = [
            ("admin@example.com", "adminpass", "Admin"),
            ("auditor@example.com", "password123", "Auditor_L1"),
            ("senior@example.com", "password123", "Auditor_L2"),
            ("manager@example.com", "password123", "Auditor_L3"),
            ("seniormgr@example.com", "password123", "Auditor_L4"),
            ("client@example.com", "password123", "Client"),
        ]
        for email, pw, role in demo:
            db_seed.add(User(email=email, password_hash=hash_password(pw), role=role, is_active=True))
        db_seed.commit()

    # Seed an example control if none
    if db_seed.query(Control).count() == 0:
        c = Control(
            name="User Access Reviews",
            control_id_tag="ITGC-001",
            audit_year=2025,
            description="Quarterly user access review for critical systems",
            control_type="ITGC",
            category="Access Management",
            frequency="Quarterly",
            status=STATUS["NOT_STARTED"],
        )
        db_seed.add(c)
        db_seed.commit()
finally:
    db_seed.close()

@router.post("/login", response_model=TokenOut)
def login(email: str, password: str, db: Session = Depends(SessionLocal)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    return TokenOut(access_token=token)

@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(SessionLocal), email: str = ""):
    # for docs/testing: not used by UI
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
