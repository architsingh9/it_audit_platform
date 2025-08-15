from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..deps import get_db, get_current_user
from ..models import Task, Project, Control
from ..schemas import TaskCreate, TaskUpdate, TaskOut
from ..rbac import require_roles

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskOut])
def list_tasks(
    project_id: Optional[int] = None,
    control_id: Optional[int] = None,
    db: Session = Depends(get_db),
    me=Depends(get_current_user)
):
    q = db.query(Task).order_by(Task.created_at.desc())
    if project_id: q = q.filter(Task.project_id == project_id)
    if control_id: q = q.filter(Task.control_id == control_id)
    return q.all()

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), me=Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"])
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.control_id and not db.query(Control).filter(Control.id == payload.control_id).first():
        raise HTTPException(status_code=404, detail="Control not found")
    t = Task(**payload.model_dump())
    db.add(t); db.commit(); db.refresh(t)
    return t

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), me=Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"])
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t: raise HTTPException(status_code=404, detail="Task not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.add(t); db.commit(); db.refresh(t)
    return t

# convenience auto-generator (simple template)
@router.post("/generate_for_control/{control_id}", response_model=List[TaskOut])
def generate_for_control(control_id: int, db: Session = Depends(get_db), me=Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"])
    c = db.query(Control).filter(Control.id == control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    templates = [
        ("Plan walkthrough & kickoff for control", "High"),
        ("Request PBC / ERL from client", "High"),
        ("Perform design assessment", "Medium"),
        ("Select samples & perform testing", "Medium"),
        ("Draft test memo & findings", "Medium"),
        ("Peer review (L2) & update", "Medium"),
        ("Manager review (L3) & finalize", "Medium"),
        ("Prepare client release (L4)", "Low"),
    ]
    out = []
    for d, p in templates:
        t = Task(project_id=c.project_id, control_id=c.id, description=d, priority=p, status="Todo")
        db.add(t); out.append(t)
    db.commit()
    for t in out: db.refresh(t)
    return out
