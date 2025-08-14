from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..deps import get_db, get_current_user
from ..models import ApprovalRequest, Control, User
from ..schemas import ApprovalRequestCreate, ApprovalRequestAction, ApprovalRequestOut
from ..config import STATUS
from ..workflow import can_transition, action_target_for_role

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.post("/", response_model=ApprovalRequestOut)
def create_approval_request(payload: ApprovalRequestCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    if me.role not in ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    control = None
    if payload.document_type == "Control":
        control = db.query(Control).filter(Control.id == payload.document_id, Control.is_deleted == False).first()  # noqa: E712
        if not control:
            raise HTTPException(status_code=404, detail="Control not found")
        payload.control_id = control.id

    active = db.query(ApprovalRequest).filter(
        ApprovalRequest.document_type == payload.document_type,
        ApprovalRequest.document_id == payload.document_id,
        ApprovalRequest.is_deleted == False,  # noqa: E712
        ApprovalRequest.status.in_([
            STATUS["PENDING_L1_REVIEW"],
            STATUS["PENDING_L2_REVIEW"],
            STATUS["PENDING_L3_REVIEW"],
            STATUS["PENDING_L4_RELEASE"],
            STATUS["REVISIONS_REQUESTED"],
        ])
    ).first()
    if active:
        raise HTTPException(status_code=400, detail=f"Active approval exists: {active.status}")

    req = ApprovalRequest(
        document_type=payload.document_type,
        document_id=payload.document_id,
        control_id=payload.control_id,
        current_level=1,
        status=STATUS["PENDING_L1_REVIEW"],
        requested_by_id=me.id,
        comments=payload.comments or "Initial request"
    )
    db.add(req)

    if control:
        control.status = STATUS["PENDING_L1_REVIEW"]
        db.add(control)

    db.commit(); db.refresh(req)
    return req

@router.get("/", response_model=List[ApprovalRequestOut])
def list_approvals(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    q = db.query(ApprovalRequest).options(joinedload(ApprovalRequest.control_obj)).filter(ApprovalRequest.is_deleted == False).order_by(ApprovalRequest.approval_date.desc())  # noqa: E712
    if me.role == "Admin":
        return q.all()
    allowed_status_by_role = {
        "Auditor_L1": [STATUS["REVISIONS_REQUESTED"]],
        "Auditor_L2": [STATUS["PENDING_L1_REVIEW"]],
        "Auditor_L3": [STATUS["PENDING_L2_REVIEW"]],
        "Auditor_L4": [STATUS["PENDING_L3_REVIEW"], STATUS["PENDING_L4_RELEASE"]],
        "Client": [],
    }
    return q.filter(ApprovalRequest.status.in_(allowed_status_by_role.get(me.role, []))).all()

@router.post("/{approval_id}/action", response_model=ApprovalRequestOut)
def act_on_approval(approval_id: int, payload: ApprovalRequestAction, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id, ApprovalRequest.is_deleted == False).first()  # noqa: E712
    if not req: raise HTTPException(status_code=404, detail="Approval request not found")

    target = action_target_for_role(me.role, payload.action)
    if not target:
        raise HTTPException(status_code=403, detail="Action not allowed for your role")

    if not can_transition(req.status, target):
        raise HTTPException(status_code=400, detail=f"Invalid transition {req.status} -> {target}")

    if payload.action in ["reject", "request_revisions"] and not (payload.comments or "").strip():
        raise HTTPException(status_code=400, detail="Comments required for this action")

    req.status = target
    req.approved_by_id = me.id
    req.approval_date = datetime.utcnow()
    req.comments = payload.comments
    is_released = (payload.action in ["release_to_client"])
    req.is_released_to_client = is_released

    if req.document_type == "Control" and req.control_id:
        control = db.query(Control).filter(Control.id == req.control_id, Control.is_deleted == False).first()  # noqa: E712
        if control:
            control.status = target
            if is_released:
                control.released_to_client = True
            db.add(control)

    db.add(req); db.commit(); db.refresh(req)
    return req
