from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models import Control
from ..schemas import ControlOut

router = APIRouter(prefix="/controls", tags=["Controls"])

@router.get("/", response_model=List[ControlOut])
def list_controls(project_id: int, q: Optional[str] = None, db: Session = Depends(get_db)):
    qset = db.query(Control).filter(Control.project_id == project_id)
    if q:
        like = f"%{q}%"
        qset = qset.filter((Control.name.ilike(like)) | (Control.control_id_tag.ilike(like)))
    return qset.order_by(Control.id).all()
