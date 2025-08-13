from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..models import User
from ..schemas import UserCreate, UserOut
from ..security import hash_password
from ..rbac import require_roles

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_roles(current_user.role, ["Admin"])
    return db.query(User).all()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_roles(current_user.role, ["Admin"])
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role, is_active=payload.is_active)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_roles(current_user.role, ["Admin"])
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u); db.commit()
    return {}
