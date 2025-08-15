from fastapi import APIRouter
router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("/")
def list_approvals():
    return []
