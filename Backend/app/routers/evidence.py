from fastapi import APIRouter
router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("/")
def list_evidence():
    return []
