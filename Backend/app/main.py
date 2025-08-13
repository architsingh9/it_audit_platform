from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, controls, evidence, approvals, client_dashboard

app = FastAPI(title="IT Audit Platform API")

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
