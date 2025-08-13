from .config import STATUS

S = STATUS  # alias

# Valid transitions
VALID_TRANSITIONS: dict[str, list[str]] = {
    S["NOT_STARTED"]: [S["EVIDENCE_REQUESTED"], S["TESTING_IN_PROGRESS"]],
    S["EVIDENCE_REQUESTED"]: [S["EVIDENCE_PROVIDED"], S["REVISIONS_REQUESTED"]],
    S["EVIDENCE_PROVIDED"]: [S["TESTING_IN_PROGRESS"], S["REVISIONS_REQUESTED"]],
    S["TESTING_IN_PROGRESS"]: [S["PENDING_L1_REVIEW"], S["REVISIONS_REQUESTED"]],
    S["PENDING_L1_REVIEW"]: [S["PENDING_L2_REVIEW"], S["REVISIONS_REQUESTED"]],
    S["PENDING_L2_REVIEW"]: [S["PENDING_L3_REVIEW"], S["REVISIONS_REQUESTED"]],
    S["PENDING_L3_REVIEW"]: [S["PENDING_L4_RELEASE"], S["REVISIONS_REQUESTED"]],
    S["PENDING_L4_RELEASE"]: [S["APPROVED_INTERNAL"], S["REVISIONS_REQUESTED"]],
    S["APPROVED_INTERNAL"]: [S["RELEASED_TO_CLIENT"]],
    S["REVISIONS_REQUESTED"]: [S["PENDING_L1_REVIEW"]],  # resubmit
}

# Role→action→target status
ROLE_ACTIONS = {
    "Admin": {
        "request_approval": S["PENDING_L1_REVIEW"],
        "approve_l1": S["PENDING_L2_REVIEW"],
        "approve_l2": S["PENDING_L3_REVIEW"],
        "approve_l3": S["PENDING_L4_RELEASE"],
        "release_l4": S["RELEASED_TO_CLIENT"],
        "reject": S["REJECTED"],
        "request_revisions": S["REVISIONS_REQUESTED"],
        "resubmit": S["PENDING_L1_REVIEW"],
    },
    "Auditor_L1": {
        "request_approval": S["PENDING_L1_REVIEW"],
        "resubmit": S["PENDING_L1_REVIEW"],
    },
    "Auditor_L2": {
        "approve": S["PENDING_L2_REVIEW"],  # approve L1
        "reject": S["REJECTED"],
        "request_revisions": S["REVISIONS_REQUESTED"],
    },
    "Auditor_L3": {
        "approve": S["PENDING_L3_REVIEW"],
        "reject": S["REJECTED"],
        "request_revisions": S["REVISIONS_REQUESTED"],
    },
    "Auditor_L4": {
        "approve": S["PENDING_L4_RELEASE"],
        "reject": S["REJECTED"],
        "request_revisions": S["REVISIONS_REQUESTED"],
        "release_to_client": S["RELEASED_TO_CLIENT"],
    },
    "Client": {},
}

def can_transition(current_status: str, target_status: str) -> bool:
    return target_status in VALID_TRANSITIONS.get(current_status, [])

def action_target_for_role(role: str, action: str) -> str | None:
    return ROLE_ACTIONS.get(role, {}).get(action)
