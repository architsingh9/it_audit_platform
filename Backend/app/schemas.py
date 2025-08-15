from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Users ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: str = Field(..., description="Role (Admin, Auditor_L1..L4, Client)")
    is_active: bool = True

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    class Config:
        from_attributes = True

# --- Projects ---
class ProjectBase(BaseModel):
    name: str
    is_active: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Controls ---
class ControlBase(BaseModel):
    project_id: Optional[int] = None
    name: str
    control_id_tag: str
    audit_year: int
    description: Optional[str] = None
    control_type: str  # 'ITGC' or 'ITAC'
    category: Optional[str] = None
    frequency: Optional[str] = None
    owner_id: Optional[int] = None

    @field_validator("control_type")
    @classmethod
    def _ctype(cls, v: str) -> str:
        if v not in ("ITGC", "ITAC"):
            raise ValueError("control_type must be 'ITGC' or 'ITAC'")
        return v

class ControlCreate(ControlBase):
    pass

class ControlUpdate(BaseModel):
    status: Optional[str] = None
    bottlenecks: Optional[str] = None
    progress_notes: Optional[str] = None
    final_report_text: Optional[str] = None
    released_to_client: Optional[bool] = None
    category: Optional[str] = None
    control_type: Optional[str] = None

class ControlOut(ControlBase):
    id: int
    status: str
    owner: Optional[UserOut] = None
    bottlenecks: Optional[str] = None
    progress_notes: Optional[str] = None
    final_report_text: Optional[str] = None
    released_to_client: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Evidence Requests ---
class EvidenceRequestBase(BaseModel):
    control_id: int
    description: str
    last_year_info: Optional[str] = None

class EvidenceRequestCreate(EvidenceRequestBase):
    pass

class EvidenceRequestOut(EvidenceRequestBase):
    id: int
    status: str
    requested_by_id: Optional[int] = None
    requested_by: Optional[UserOut] = None
    requested_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Evidence ---
class EvidenceOut(BaseModel):
    id: int
    evidence_request_id: int
    filename: str
    stored_path: str
    file_hash: Optional[str] = None
    file_type: Optional[str] = None
    version_number: int
    uploaded_by_id: int
    uploaded_at: datetime
    description: Optional[str] = None
    class Config:
        from_attributes = True

# --- Approvals ---
class ApprovalRequestCreate(BaseModel):
    document_type: str
    document_id: int
    control_id: Optional[int] = None
    comments: Optional[str] = None

class ApprovalRequestAction(BaseModel):
    action: str
    comments: Optional[str] = None

class ApprovalRequestOut(BaseModel):
    id: int
    document_type: str
    document_id: int
    control_id: Optional[int] = None
    control_obj: Optional[ControlOut] = None
    current_level: int
    status: str
    requested_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    approval_date: datetime
    comments: Optional[str] = None
    is_released_to_client: bool
    class Config:
        from_attributes = True

# --- Tasks ---
class TaskBase(BaseModel):
    project_id: int
    control_id: Optional[int] = None
    description: str
    priority: str = "Medium"
    status: str = "Todo"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    control_id: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
