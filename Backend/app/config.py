import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "change_me_dev_only")
ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
JWT_EXPIRE_DELTA = timedelta(minutes=JWT_EXPIRE_MINUTES)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audit.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")

ROLES = ("Admin", "Auditor_L1", "Auditor_L2", "Auditor_L3", "Auditor_L4", "Client")

STATUS = {
    "NOT_STARTED": "Not Started",
    "EVIDENCE_REQUESTED": "Evidence Requested",
    "EVIDENCE_PROVIDED": "Evidence Provided",
    "TESTING_IN_PROGRESS": "Testing In Progress",
    "PENDING_L1_REVIEW": "Pending L1 Review",
    "PENDING_L2_REVIEW": "Pending L2 Review",
    "PENDING_L3_REVIEW": "Pending L3 Review",
    "PENDING_L4_RELEASE": "Pending L4 Release",
    "APPROVED_INTERNAL": "Approved Internally",
    "REVISIONS_REQUESTED": "Revisions Requested",
    "REJECTED": "Rejected",
    "RELEASED_TO_CLIENT": "Released to Client",
}

ITGC_CATEGORIES = [
    "Access Management",
    "Change Management",
    "Backup & Recovery",
    "Operations",
    "Security Monitoring",
    "Incident Management",
]
ITAC_CATEGORIES = [
    "Input Controls", "Processing Controls", "Output Controls"
]
FREQUENCIES = ["Daily", "Weekly", "Monthly", "Quarterly", "Annually", "Ad-hoc"]
