from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import User, Control, Project, Task
from .security import hash_password
from .config import STATUS
from .routers import auth, users, controls, evidence, approvals, client_dashboard
from .routers import projects, tasks
from fastapi import FastAPI
from .routers import auth, controls, tasks 


app = FastAPI(title="IT Audit Platform")

app.include_router(auth.router)
app.include_router(controls.router)
app.include_router(tasks.router) 

def seed_demo_data(db: Session):
    if db.query(User).count() == 0:
        for email, pw, role in [
            ("admin@example.com", "adminpass", "Admin"),
            ("auditor@example.com", "password123", "Auditor_L1"),
            ("senior@example.com", "password123", "Auditor_L2"),
            ("manager@example.com", "password123", "Auditor_L3"),
            ("seniormgr@example.com", "password123", "Auditor_L4"),
            ("client@example.com", "password123", "Client"),
        ]:
            db.add(User(email=email, password_hash=hash_password(pw), role=role, is_active=True))
        db.commit()

    if db.query(Project).count() == 0:
        p = Project(name="FY25 Cloud ERP – Global", is_active=True)
        db.add(p); db.commit(); db.refresh(p)

        if db.query(Control).count() == 0:
            c = Control(
                project_id=p.id,
                name="User Access Reviews",
                control_id_tag="ITGC-001",
                audit_year=2025,
                description="Quarterly user access review for critical systems",
                control_type="ITGC",
                category="Access Management",
                frequency="Quarterly",
                status=STATUS["NOT_STARTED"],
            )
            db.add(c); db.commit(); db.refresh(c)
            # a couple of demo tasks
            for d, pr in [("Kickoff meeting with client", "High"), ("Prepare ERL list", "High")]:
                db.add(Task(project_id=p.id, control_id=c.id, description=d, priority=pr))
            db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
        yield
    finally:
        db.close()

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
app.include_router(projects.router)
app.include_router(controls.router)
app.include_router(tasks.router)
app.include_router(evidence.router)
app.include_router(approvals.router)
app.include_router(client_dashboard.router)
