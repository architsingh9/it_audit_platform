from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..models import Project, Control
from ..schemas import ProjectCreate, ProjectUpdate, ProjectOut
from ..rbac import require_roles

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), me=Depends(get_current_user)):
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), me=Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L3"])
    if db.query(Project).filter(Project.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Project name exists")
    p = Project(**payload.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), me=Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L3"])
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p: raise HTTPException(status_code=404, detail="Project not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.add(p); db.commit(); db.refresh(p)
    return p
