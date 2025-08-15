from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..db import SessionLocal
from ..models import Control, Project
from ..schemas import ControlOut

router = APIRouter(prefix="/controls", tags=["Controls"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ControlOut])
def list_controls(
    project_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Control)
    if project_id is not None:
        # hard guard: 404 if bad project_id
        proj = db.query(Project).get(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
        query = query.filter(Control.project_id == project_id)

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Control.name.ilike(like), Control.control_id_tag.ilike(like)))

    return query.order_by(Control.id.asc()).all()
