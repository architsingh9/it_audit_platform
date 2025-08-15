from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
from .config import STATUS

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    controls: Mapped[list["Control"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Control(Base):
    __tablename__ = "controls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["Project"] = relationship(back_populates="controls")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    control_id_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    audit_year: Mapped[int] = mapped_column(Integer, default=datetime.utcnow().year)
    status: Mapped[str] = mapped_column(String(50), default=STATUS["NOT_STARTED"])
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'ITGC' or 'ITAC'
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])

    bottlenecks: Mapped[str | None] = mapped_column(Text, default="")
    progress_notes: Mapped[str | None] = mapped_column(Text, default="")
    final_report_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    released_to_client: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence_requests: Mapped[list["EvidenceRequest"]] = relationship(back_populates="control", cascade="all, delete-orphan")
    approval_requests: Mapped[list["ApprovalRequest"]] = relationship(back_populates="control_obj", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="control", cascade="all, delete-orphan")

class EvidenceRequest(Base):
    __tablename__ = "evidence_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"))
    control: Mapped["Control"] = relationship(back_populates="evidence_requests")

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending_client")
    last_year_info: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requested_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    requested_by: Mapped["User"] = relationship(foreign_keys=[requested_by_id])
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidences: Mapped[list["Evidence"]] = relationship(back_populates="request", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_request_id: Mapped[int] = mapped_column(ForeignKey("evidence_requests.id"))
    request: Mapped["EvidenceRequest"] = relationship(back_populates="evidences")

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_by: Mapped["User"] = relationship(foreign_keys=[uploaded_by_id])
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_id: Mapped[int] = mapped_column(Integer, nullable=False)
    control_id: Mapped[int | None] = mapped_column(ForeignKey('controls.id'), nullable=True)
    control_obj: Mapped["Control"] = relationship(foreign_keys=[control_id], back_populates="approval_requests")

    current_level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=STATUS["PENDING_L1_REVIEW"])
    requested_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    requested_by: Mapped["User"] = relationship(foreign_keys=[requested_by_id])
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_by: Mapped["User"] = relationship(foreign_keys=[approved_by_id])
    approval_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_released_to_client: Mapped[bool] = mapped_column(Boolean, default=False)

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    control_id: Mapped[int | None] = mapped_column(ForeignKey("controls.id"), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    control: Mapped["Control"] = relationship(back_populates="tasks")

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), default="Medium")
    status: Mapped[str] = mapped_column(String(20), default="Todo")
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_to: Mapped["User"] = relationship(foreign_keys=[assigned_to_id])

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
