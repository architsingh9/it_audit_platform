from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import Counter
from ..db import get_db
from ..models import Control

router = APIRouter(prefix="/client_dashboard", tags=["Client Dashboard"])

@router.get("/")
def client_dashboard(project_id: int, db: Session = Depends(get_db)):
    controls = db.query(Control).filter(Control.project_id == project_id).all()
    in_progress = sum(1 for c in controls if c.status and c.status.lower() not in ("not started", "complete", "completed"))
    awaiting_client = sum(1 for c in controls if (c.progress_notes or "").lower().find("client") >= 0)
    with_bnecks = sum(1 for c in controls if c.bottlenecks)
    counts = Counter()
    for c in controls:
        if c.bottlenecks:
            for word in c.bottlenecks.lower().split(","):
                word = word.strip()
                if word:
                    counts[word] += 1
    top = [{"label": k, "count": v} for k, v in counts.most_common(10)]
    return {
        "metrics": {
            "total_controls": len(controls),
            "in_progress": in_progress,
            "awaiting_client": awaiting_client,
            "with_bottlenecks": with_bnecks,
        },
        "top_bottlenecks": top,
    }
