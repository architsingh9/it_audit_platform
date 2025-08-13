from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

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

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Controls ---
class ControlBase(BaseModel):
    name: str
    control_id_tag: str
    audit_year: int
    description: Optional[str] = None
    control_type: str
    category: Optional[str] = None
    frequency: Optional[str] = None
    owner_id: Optional[int] = None

class ControlCreate(ControlBase):
    pass

class ControlUpdate(BaseModel):
    status: Optional[str] = None
    bottlenecks: Optional[str] = None
    progress_notes: Optional[str] = None
    final_report_text: Optional[str] = None
    released_to_client: Optional[bool] = None

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
