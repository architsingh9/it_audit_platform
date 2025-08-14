from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..models import Control, User
from ..schemas import ControlOut

router = APIRouter(prefix="/client_dashboard", tags=["Client"])

@router.get("/", response_model=List[ControlOut])
def get_client_controls(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    if me.role == "Client":
        controls = db.query(Control).filter(Control.owner_id == me.id, Control.is_deleted == False).all()  # noqa: E712
    else:
        controls = db.query(Control).filter(Control.is_deleted == False).all()  # noqa: E712
    outs = []
    for c in controls:
        d = ControlOut.model_validate(c).model_dump()
        if me.role == "Client" and not c.released_to_client:
            d["final_report_text"] = None
        outs.append(d)
    return outs
