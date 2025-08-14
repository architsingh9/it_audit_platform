from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .routers import auth, users, controls, evidence, approvals, client_dashboard
from .models import User, Control
from .security import hash_password
from .config import STATUS

def seed_demo_data(db: Session):
    if db.query(User).count() == 0:
        demo = [
            ("admin@example.com", "adminpass", "Admin"),
            ("auditor@example.com", "password123", "Auditor_L1"),
            ("senior@example.com", "password123", "Auditor_L2"),
            ("manager@example.com", "password123", "Auditor_L3"),
            ("seniormgr@example.com", "password123", "Auditor_L4"),
            ("client@example.com", "password123", "Client"),
        ]
        for email, pw, role in demo:
            db.add(User(email=email, password_hash=hash_password(pw), role=role, is_active=True))
        db.commit()
    if db.query(Control).count() == 0:
        c = Control(
            name="User Access Reviews",
            control_id_tag="ITGC-001",
            audit_year=2025,
            description="Quarterly user access review for critical systems",
            control_type="ITGC",
            category="Access Management",
            frequency="Quarterly",
            status=STATUS["NOT_STARTED"],
        )
        db.add(c)
        db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables once per process and seed demo data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield
    # teardown hooks if needed

app = FastAPI(title="IT Audit Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(controls.router)
app.include_router(evidence.router)
app.include_router(approvals.router)
app.include_router(client_dashboard.router)
