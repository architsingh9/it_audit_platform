from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..deps import get_db, get_current_user
from ..models import Control, EvidenceRequest, User
from ..schemas import ControlCreate, ControlOut, ControlUpdate, EvidenceRequestCreate, EvidenceRequestOut
from ..rbac import require_roles
from ..config import STATUS, ITGC_CATEGORIES, ITAC_CATEGORIES, FREQUENCIES

router = APIRouter(prefix="/controls", tags=["Controls"])

@router.post("/", response_model=ControlOut, status_code=status.HTTP_201_CREATED)
def create_control(payload: ControlCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1"])
    if db.query(Control).filter(Control.control_id_tag == payload.control_id_tag).first():
        raise HTTPException(status_code=400, detail="Control ID Tag exists")
    if payload.control_type not in ("ITGC", "ITAC"):
        raise HTTPException(status_code=400, detail="Invalid control_type")
    if payload.control_type == "ITGC" and payload.category and payload.category not in ITGC_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid ITGC category")
    if payload.control_type == "ITAC" and payload.category and payload.category not in ITAC_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid ITAC category")
    if payload.frequency and payload.frequency not in FREQUENCIES:
        raise HTTPException(status_code=400, detail=f"Invalid frequency")
    c = Control(**payload.model_dump(), status=STATUS["NOT_STARTED"])
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("/", response_model=List[ControlOut])
def list_controls(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    controls = db.query(Control).options(joinedload(Control.owner)).order_by(Control.audit_year.desc(), Control.created_at.desc()).all()
    outs = []
    for c in controls:
        d = ControlOut.model_validate(c).model_dump()
        if me.role == "Client" and not c.released_to_client:
            d["final_report_text"] = None
        outs.append(d)
    return outs

@router.get("/{control_id}", response_model=ControlOut)
def get_control(control_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    c = db.query(Control).options(joinedload(Control.owner)).filter(Control.id == control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    d = ControlOut.model_validate(c).model_dump()
    if me.role == "Client" and not c.released_to_client:
        d["final_report_text"] = None
    return d

@router.put("/{control_id}", response_model=ControlOut)
def update_control(control_id: int, payload: ControlUpdate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"])
    c = db.query(Control).filter(Control.id == control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.post("/requests", response_model=EvidenceRequestOut, status_code=status.HTTP_201_CREATED)
def create_evidence_request(payload: EvidenceRequestCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"])
    c = db.query(Control).filter(Control.id == payload.control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    r = EvidenceRequest(control_id=c.id, description=payload.description, last_year_info=payload.last_year_info, requested_by_id=me.id, status="pending_client")
    db.add(r); db.commit(); db.refresh(r)
    return r

@router.get("/{control_id}/requests", response_model=List[EvidenceRequestOut])
def list_requests(control_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    c = db.query(Control).filter(Control.id == control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    reqs = db.query(EvidenceRequest).filter(EvidenceRequest.control_id == control_id).all()
    return reqs

@router.post("/{control_id}/generate_pbc_ai")
def generate_pbc_ai(control_id: int, audit_context: str = Form(...), db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    require_roles(me.role, ["Admin", "Auditor_L1"])
    c = db.query(Control).filter(Control.id == control_id).first()
    if not c: raise HTTPException(status_code=404, detail="Control not found")
    simulated = f"""
AI-Generated PBC for {c.name} ({c.control_id_tag})
Context: {audit_context}

1) Access Control Policy (PDF/DOCX)
2) Quarterly Access Review Logs (XLSX/CSV)
3) Change Management Sample (5 recent with approvals & testing)
"""
    return {"generated_pbc": simulated}
