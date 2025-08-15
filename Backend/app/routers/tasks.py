from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models import Task
from ..schemas import TaskOut

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.id).all()
