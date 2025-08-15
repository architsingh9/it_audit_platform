from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import Base, engine, SessionLocal
from .models import User, Project, Control
from .security import hash_password
from .routers import auth, controls, tasks, approvals, evidence, client_dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                password_hash=hash_password("adminpass"),
                role="Admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
        proj = db.query(Project).filter(Project.name == "FY25 Cloud ERP - Global").first()
        if not proj:
            proj = Project(name="FY25 Cloud ERP - Global", is_active=True)
            db.add(proj)
            db.commit()
        if not db.query(Control).first():
            db.add(Control(
                project_id=proj.id,
                name="User Access Reviews",
                control_id_tag="ITGC-001",
                audit_year=2025,
                description="Quarterly user access review for critical systems",
                control_type="ITGC",
                category="Access Management",
                frequency="Quarterly",
                status="Not Started",
                released_to_client=False
            ))
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(controls.router)
app.include_router(tasks.router)
app.include_router(approvals.router)
app.include_router(evidence.router)
app.include_router(client_dashboard.router)
