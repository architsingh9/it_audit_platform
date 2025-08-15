from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Task, Project
from ..schemas import TaskOut

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[TaskOut])
def list_tasks(
    project_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if project_id is not None:
        proj = db.query(Project).get(project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")
        query = query.filter(Task.project_id == project_id)
    return query.order_by(Task.id.asc()).all()
