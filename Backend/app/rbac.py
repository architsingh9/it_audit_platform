from fastapi import HTTPException, status

def require_roles(user_role: str, allowed_roles: list[str]):
    if user_role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
