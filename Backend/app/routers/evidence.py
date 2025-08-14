import os, hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..deps import get_db, get_current_user
from ..models import EvidenceRequest, Evidence, Control, User
from ..schemas import EvidenceOut
from ..utils.file_utils import ensure_dir, allowed_file, get_ext
from ..config import UPLOAD_DIR

router = APIRouter(prefix="/evidence", tags=["Evidence"])
ALLOWED_EXT = {"pdf", "doc", "docx", "xlsx", "xls", "csv", "txt", "png", "jpg", "jpeg"}

@router.post("/upload/{request_id}", response_model=EvidenceOut, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    request_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user)
):
    req = db.query(EvidenceRequest).options(joinedload(EvidenceRequest.control)).filter(
        EvidenceRequest.id == request_id, EvidenceRequest.is_deleted == False  # noqa: E712
    ).first()
    if not req: raise HTTPException(status_code=404, detail="Evidence Request not found")

    ext = get_ext(file.filename)
    if not allowed_file(file.filename, ALLOWED_EXT):
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed")

    control_tag = req.control.control_id_tag
    control_dir = os.path.join(UPLOAD_DIR, control_tag)
    ensure_dir(control_dir)

    latest = db.query(Evidence).filter(Evidence.evidence_request_id == req.id, Evidence.is_deleted == False).order_by(Evidence.version_number.desc()).first()  # noqa: E712
    next_version = (latest.version_number + 1) if latest else 1

    base, _ = os.path.splitext(file.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_name = f"{base}_v{next_version}_{timestamp}.{ext}"
    stored_path = os.path.join(control_dir, unique_name)

    content = await file.read()
    with open(stored_path, "wb") as outf:
        outf.write(content)
    file_hash = hashlib.sha256(content).hexdigest()

    ev = Evidence(
        evidence_request_id=req.id,
        filename=file.filename,
        stored_path=stored_path,
        file_hash=file_hash,
        file_type=ext.upper(),
        version_number=next_version,
        uploaded_by_id=me.id,
        description=description
    )
    db.add(ev)

    req.status = "provided"
    db.add(req)

    db.commit(); db.refresh(ev)
    return ev

@router.get("/download/{evidence_id}")
def download_evidence(evidence_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    ev = db.query(Evidence).options(
        joinedload(Evidence.request).joinedload(EvidenceRequest.control)
    ).filter(Evidence.id == evidence_id, Evidence.is_deleted == False).first()  # noqa: E712
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")

    can_download = False
    if me.role in ["Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4"]:
        can_download = True
    elif me.role == "Client":
        if ev.uploaded_by_id == me.id:
            can_download = True
        elif ev.request.control and ev.request.control.owner_id == me.id and ev.request.control.released_to_client:
            can_download = True

    if not can_download:
        raise HTTPException(status_code=403, detail="No permission")

    if not os.path.exists(ev.stored_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=ev.stored_path, filename=ev.filename)

@router.get("/{request_id}/list", response_model=List[EvidenceOut])
def list_evidence(request_id: int, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    req = db.query(EvidenceRequest).filter(EvidenceRequest.id == request_id, EvidenceRequest.is_deleted == False).first()  # noqa: E712
    if not req: raise HTTPException(status_code=404, detail="Evidence Request not found")
    items = db.query(Evidence).filter(Evidence.evidence_request_id == request_id, Evidence.is_deleted == False).all()  # noqa: E712
    return items
